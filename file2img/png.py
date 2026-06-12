"""Small PNG reader/writer for file2img's own RGB images."""

from __future__ import annotations

import binascii
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def write_rgb_png(
    path: str,
    width: int,
    height: int,
    pixels: bytes,
    text: dict[str, str] | None = None,
) -> None:
    if len(pixels) != width * height * 3:
        raise ValueError("pixel data size does not match image dimensions")

    scanlines = bytearray()
    row_size = width * 3
    for y in range(height):
        scanlines.append(0)
        start = y * row_size
        scanlines.extend(pixels[start : start + row_size])

    chunks = [
        _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
    ]

    for key, value in (text or {}).items():
        chunks.append(_chunk(b"tEXt", key.encode("latin-1") + b"\x00" + value.encode("utf-8")))

    chunks.append(_chunk(b"IDAT", zlib.compress(bytes(scanlines))))
    chunks.append(_chunk(b"IEND", b""))

    with open(path, "wb") as image_file:
        image_file.write(PNG_SIGNATURE)
        image_file.write(b"".join(chunks))


def read_rgb_png(path: str) -> tuple[int, int, bytes, dict[str, str]]:
    with open(path, "rb") as image_file:
        data = image_file.read()

    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")

    offset = len(PNG_SIGNATURE)
    width = 0
    height = 0
    color_type = None
    bit_depth = None
    idat = bytearray()
    text: dict[str, str] = {}

    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length

        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"tEXt":
            key, _, value = payload.partition(b"\x00")
            text[key.decode("latin-1")] = value.decode("utf-8")
        elif kind == b"IEND":
            break

    if bit_depth != 8 or color_type != 2:
        raise ValueError("only 8-bit RGB PNG files are supported right now")

    raw = zlib.decompress(bytes(idat))
    row_size = width * 3
    pixels = bytearray()
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        if filter_type != 0:
            raise ValueError("only PNG filter type 0 is supported right now")
        pixels.extend(raw[cursor : cursor + row_size])
        cursor += row_size

    return width, height, bytes(pixels), text


def _chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = binascii.crc32(kind)
    checksum = binascii.crc32(payload, checksum)
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum & 0xFFFFFFFF)
