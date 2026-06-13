import hashlib

import pytest

from file2img.codec import decode_file, encode_file
from file2img.patterns import available_patterns
from file2img.png import read_rgb_png, write_rgb_png


@pytest.mark.parametrize("pattern", available_patterns())
def test_pattern_round_trip(tmp_path, pattern):
    source = tmp_path / "source.bin"
    source.write_bytes(bytes(range(256)) + b"hello from file2img")

    original_checksum = hashlib.sha256(source.read_bytes()).hexdigest()
    image = tmp_path / f"{pattern}.png"
    restored = tmp_path / f"{pattern}.bin"

    encode_file(str(source), str(image), pattern)
    decode_file(str(image), str(restored))

    assert hashlib.sha256(restored.read_bytes()).hexdigest() == original_checksum


def test_decode_works_when_png_text_metadata_is_missing(tmp_path):
    source = tmp_path / "source.bin"
    image = tmp_path / "source.png"
    stripped_image = tmp_path / "stripped.png"
    restored = tmp_path / "restored.bin"
    source.write_bytes(b"metadata fallback test\n" * 20)

    encode_file(str(source), str(image), "row_reverse")
    width, height, pixels, _ = read_rgb_png(str(image))
    write_rgb_png(str(stripped_image), width, height, pixels)

    decode_file(str(stripped_image), str(restored))

    assert restored.read_bytes() == source.read_bytes()
