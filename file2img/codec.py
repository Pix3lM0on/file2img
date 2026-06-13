"""Encode files into images and decode them back."""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct

from .patterns import iter_pattern
from .png import read_rgb_png, write_rgb_png

METADATA_KEY = "file2img"
VERSION = 1
HEADER_MAGIC = b"F2IMG\x00\x01\x00"
HEADER_PREFIX_SIZE = len(HEADER_MAGIC) + 4


def encode_file(input_path: str, output_path: str, pattern: str = "spiral") -> None:
    with open(input_path, "rb") as input_file:
        data = input_file.read()

    metadata = {
        "version": VERSION,
        "filename": os.path.basename(input_path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "pattern": pattern,
    }
    header = _metadata_to_header(metadata)
    width, height = _image_size(len(data), len(header))
    pixels = _bytes_to_pixels(data, width, height, pattern, header)
    write_rgb_png(output_path, width, height, pixels, {METADATA_KEY: json.dumps(metadata)})


def decode_file(input_path: str, output_path: str | None = None) -> str:
    width, height, pixels, text = read_rgb_png(input_path)
    metadata, header_pixels = _read_embedded_metadata(pixels, width, height)

    if metadata is None:
        if METADATA_KEY not in text:
            raise ValueError("missing file2img metadata")
        metadata = json.loads(text[METADATA_KEY])
        header_pixels = 0

    if metadata.get("version") != VERSION:
        raise ValueError(f"unsupported file2img version: {metadata.get('version')!r}")

    output_path = output_path or metadata["filename"]
    data = _pixels_to_bytes(
        pixels,
        width,
        height,
        metadata["size"],
        metadata["pattern"],
        header_pixels,
    )

    if hashlib.sha256(data).hexdigest() != metadata["sha256"]:
        raise ValueError("decoded file checksum does not match metadata")

    with open(output_path, "wb") as output_file:
        output_file.write(data)

    return output_path


def _metadata_to_header(metadata: dict[str, object]) -> bytes:
    payload = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    header = HEADER_MAGIC + struct.pack(">I", len(payload)) + payload
    return header + bytes((-len(header)) % 3)


def _read_embedded_metadata(
    pixels: bytes,
    width: int,
    height: int,
) -> tuple[dict[str, object] | None, int]:
    if len(pixels) < HEADER_PREFIX_SIZE or not pixels.startswith(HEADER_MAGIC):
        return None, 0

    payload_size = struct.unpack(">I", pixels[len(HEADER_MAGIC) : HEADER_PREFIX_SIZE])[0]
    header_size = HEADER_PREFIX_SIZE + payload_size
    padded_header_size = header_size + (-header_size) % 3

    if padded_header_size > len(pixels):
        raise ValueError("file2img metadata header is incomplete")

    metadata = json.loads(pixels[HEADER_PREFIX_SIZE:header_size].decode("utf-8"))
    header_pixels = math.ceil(padded_header_size / 3)
    if header_pixels > width * height:
        raise ValueError("file2img metadata header is too large for this image")

    return metadata, header_pixels


def _image_size(data_size: int, header_size: int = 0) -> tuple[int, int]:
    pixel_count = math.ceil(header_size / 3) + math.ceil(data_size / 3)
    pixel_count = max(1, pixel_count)
    width = math.ceil(math.sqrt(pixel_count))
    height = math.ceil(pixel_count / width)
    return width, height


def _bytes_to_pixels(data: bytes, width: int, height: int, pattern: str, header: bytes = b"") -> bytes:
    padded = data + bytes((-len(data)) % 3)
    source_pixels = [padded[index : index + 3] for index in range(0, len(padded), 3)]
    output = bytearray(width * height * 3)
    output[: len(header)] = header
    header_pixels = math.ceil(len(header) / 3)

    for source_pixel, (x, y) in zip(
        source_pixels,
        _iter_payload_pixels(pattern, width, height, header_pixels),
        strict=False,
    ):
        index = (y * width + x) * 3
        output[index : index + 3] = source_pixel

    return bytes(output)


def _pixels_to_bytes(
    pixels: bytes,
    width: int,
    height: int,
    size: int,
    pattern: str,
    header_pixels: int = 0,
) -> bytes:
    output = bytearray()

    for x, y in _iter_payload_pixels(pattern, width, height, header_pixels):
        index = (y * width + x) * 3
        output.extend(pixels[index : index + 3])
        if len(output) >= size:
            break

    return bytes(output[:size])


def _iter_payload_pixels(
    pattern: str,
    width: int,
    height: int,
    header_pixels: int,
):
    header_coordinates = {(index % width, index // width) for index in range(header_pixels)}

    for x, y in iter_pattern(pattern, width, height):
        if (x, y) not in header_coordinates:
            yield x, y
