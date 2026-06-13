from file2img.cli import main


def test_help_mentions_pattern_options(capsys):
    try:
        main(["-h"])
    except SystemExit as error:
        assert error.code == 0

    help_text = capsys.readouterr().out
    assert "--pattern=row" in help_text
    assert "-p spiral_reverse" in help_text


def test_encode_accepts_long_pattern_option(tmp_path):
    source = tmp_path / "source.txt"
    image = tmp_path / "source.png"
    restored = tmp_path / "restored.txt"
    source.write_text("pattern test\n")

    assert main(["encode", str(source), str(image), "--pattern=row"]) == 0
    assert main(["decode", str(image), str(restored)]) == 0
    assert restored.read_text() == source.read_text()


def test_encode_accepts_short_pattern_option(tmp_path):
    source = tmp_path / "source.txt"
    image = tmp_path / "source.png"
    restored = tmp_path / "restored.txt"
    source.write_text("short pattern test\n")

    assert main(["encode", str(source), str(image), "-p", "row_reverse"]) == 0
    assert main(["decode", str(image), str(restored)]) == 0
    assert restored.read_text() == source.read_text()
