"""Encode files into images and decode them back."""

from __future__ import annotations

import hashlib
import json
import math
import os

from .patterns import iter_pattern
from .png import read_rgb_png, write_rgb_png

METADATA_KEY = "file2img"
VERSION = 1


def encode_file(input_path: str, output_path: str, pattern: str = "spiral") -> None:
    with open(input_path, "rb") as input_file:
        data = input_file.read()

    width, height = _image_size(len(data))
    pixels = _bytes_to_pixels(data, width, height, pattern)
    metadata = {
        "version": VERSION,
        "filename": os.path.basename(input_path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "pattern": pattern,
    }
    write_rgb_png(output_path, width, height, pixels, {METADATA_KEY: json.dumps(metadata)})


def decode_file(input_path: str, output_path: str | None = None) -> str:
    width, height, pixels, text = read_rgb_png(input_path)
    if METADATA_KEY not in text:
        raise ValueError("missing file2img metadata")

    metadata = json.loads(text[METADATA_KEY])
    if metadata.get("version") != VERSION:
        raise ValueError(f"unsupported file2img version: {metadata.get('version')!r}")

    output_path = output_path or metadata["filename"]
    data = _pixels_to_bytes(pixels, width, height, metadata["size"], metadata["pattern"])

    if hashlib.sha256(data).hexdigest() != metadata["sha256"]:
        raise ValueError("decoded file checksum does not match metadata")

    with open(output_path, "wb") as output_file:
        output_file.write(data)

    return output_path


def _image_size(data_size: int) -> tuple[int, int]:
    pixel_count = max(1, math.ceil(data_size / 3))
    width = math.ceil(math.sqrt(pixel_count))
    height = math.ceil(pixel_count / width)
    return width, height


def _bytes_to_pixels(data: bytes, width: int, height: int, pattern: str) -> bytes:
    padded = data + bytes((-len(data)) % 3)
    source_pixels = [padded[index : index + 3] for index in range(0, len(padded), 3)]
    output = bytearray(width * height * 3)

    for source_pixel, (x, y) in zip(source_pixels, iter_pattern(pattern, width, height), strict=False):
        index = (y * width + x) * 3
        output[index : index + 3] = source_pixel

    return bytes(output)


def _pixels_to_bytes(pixels: bytes, width: int, height: int, size: int, pattern: str) -> bytes:
    output = bytearray()

    for x, y in iter_pattern(pattern, width, height):
        index = (y * width + x) * 3
        output.extend(pixels[index : index + 3])
        if len(output) >= size:
            break

    return bytes(output[:size])
