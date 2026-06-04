
from quick_web_enum.cli import main


def test_check_requires_a_target(capsys):
    try:
        main(["check"])
    except SystemExit as exc:
        assert str(exc) == "at least one target or --input-file is required"
    else:  # pragma: no cover
        raise AssertionError("expected SystemExit")


def test_paths_command_writes_empty_csv_for_unreachable_target(tmp_path):
    wordlist = tmp_path / "words.txt"
    wordlist.write_text("admin\nhealth\n", encoding="utf-8")
    output_dir = tmp_path / "out"

    code = main([
        "paths",
        "127.0.0.1:9",
        "-w",
        str(wordlist),
        "-o",
        str(output_dir),
        "--timeout",
        "0.1",
    ])

    assert code == 0
    summary = output_dir / "summary.csv"
    assert summary.exists()
    assert summary.read_text(encoding="utf-8").splitlines()[0] == "url,status,size,content_type,title_or_error"
