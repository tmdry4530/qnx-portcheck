"""CLI behavior and output checks."""
from pathlib import Path
import pytest
from qnx_portcheck.cli import main


def test_scan_exit_thresholds(capsys, tmp_path: Path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    assert main(["scan", str(fixtures), "--fail-on", "never"]) == 0
    assert "finding(s):" in capsys.readouterr().out
    assert main(["scan", str(fixtures / "c" / "epoll_pos.c")]) == 0
    assert main(["scan", str(fixtures / "c" / "linux_header_pos.c")]) == 1
    warning_only = tmp_path / "warning-only"
    warning_only.mkdir()
    (warning_only / "warning.c").write_text('#include <sys/epoll.h>\n')
    assert main(["scan", str(warning_only)]) == 0
    assert main(["scan", str(warning_only), "--fail-on", "warning"]) == 1
    assert main(["scan", str(warning_only), "--fail-on", "never"]) == 0
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "clean.c").write_text("int main(void) { return 0; }\n")
    assert main(["scan", str(clean)]) == 0
    assert main(["scan", str(tmp_path / "missing")]) == 2
    assert "path does not exist" in capsys.readouterr().err
    with pytest.raises(SystemExit) as bad_format:
        main(["scan", str(clean), "--format", "invalid"])
    assert bad_format.value.code == 2


def test_output_version_and_commands(capsys, tmp_path: Path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    out = tmp_path / "report.json"
    assert main(["scan", str(fixtures), "--format", "json", "--out", str(out),
                 "--fail-on", "never"]) == 0
    assert '"findings"' in out.read_text()
    with pytest.raises(SystemExit) as help_exit:
        main(["--help"])
    assert help_exit.value.code == 0
    help_text = capsys.readouterr().out
    assert "scaffold" in help_text and "lint-buildfile" in help_text
    with pytest.raises(SystemExit) as version_exit:
        main(["--version"])
    assert version_exit.value.code == 0
