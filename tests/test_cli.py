"""CLI behavior and output checks."""
from pathlib import Path
import pytest
from qnx_portcheck.cli import main

def test_cli(capsys, tmp_path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    assert main(["scan", str(fixtures)]) == 0
    assert "finding(s):" in capsys.readouterr().out
    assert main(["scan", str(fixtures / "c" / "epoll_pos.c")]) == 0
    assert main(["scan", str(fixtures), "--fail-on", "error"]) == 1
    assert main(["scan", str(tmp_path / "missing")]) == 2
    assert "path does not exist" in capsys.readouterr().err
    out = tmp_path / "report.json"
    assert main(["scan", str(fixtures), "--format", "json", "--out", str(out)]) == 0
    assert '"findings"' in out.read_text()
    with pytest.raises(SystemExit) as version_exit:
        main(["--version"])
    assert version_exit.value.code == 0
