import hashlib

from file2img.codec import decode_file, encode_file
from file2img.patterns import available_patterns


def test_all_patterns_round_trip(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(bytes(range(256)) + b"hello from file2img")

    original_checksum = hashlib.sha256(source.read_bytes()).hexdigest()

    for pattern in available_patterns():
        image = tmp_path / f"{pattern}.png"
        restored = tmp_path / f"{pattern}.bin"

        encode_file(str(source), str(image), pattern)
        decode_file(str(image), str(restored))

        assert hashlib.sha256(restored.read_bytes()).hexdigest() == original_checksum
