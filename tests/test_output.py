"""Output newline behavior across report commands."""
import json
import os
from pathlib import Path
import subprocess
import sys

from qnx_portcheck.cli import main
from qnx_portcheck.output import emit


ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples" / "linux-daemon"


def _one_newline(text: str) -> bool:
    return text.endswith("\n") and not text.endswith("\n\n")


def test_scan_json_sarif_stdout_and_file(capsys, tmp_path):
    for report_format in ("json", "sarif"):
        assert main(["scan", str(EXAMPLE), "--format", report_format, "--fail-on", "never"]) == 0
        stdout = capsys.readouterr().out
        assert _one_newline(stdout)
        json.loads(stdout)

        target = tmp_path / f"{report_format}.json"
        assert main(["scan", str(EXAMPLE), "--format", report_format, "--out", str(target),
                    "--fail-on", "never"]) == 0
        captured = capsys.readouterr()
        assert captured.out == ""
        contents = target.read_text(encoding="utf-8")
        assert _one_newline(contents)
        json.loads(contents)


def test_scan_text_has_single_newline_and_no_blank_lines(capsys, tmp_path):
    assert main(["scan", str(EXAMPLE), "--fail-on", "never"]) == 0
    findings = capsys.readouterr().out
    assert _one_newline(findings)
    assert "\n\n" not in findings

    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "clean.c").write_text("int main(void) { return 0; }\n", encoding="utf-8")
    assert main(["scan", str(clean), "--fail-on", "never"]) == 0
    clean_output = capsys.readouterr().out
    assert _one_newline(clean_output)
    assert "\n\n" not in clean_output


def test_lint_buildfile_empty_text_and_json(capsys):
    buildfile = EXAMPLE / "qnx" / "filewatchd.build"
    assert main(["lint-buildfile", str(buildfile)]) == 0
    assert capsys.readouterr().out == ""
    assert main(["lint-buildfile", str(buildfile), "--format", "json"]) == 0
    assert capsys.readouterr().out == "[]\n"


def test_emit_normalizes_newlines_and_empty_files(capsys, tmp_path):
    emit("")
    assert capsys.readouterr().out == ""
    emit("x\n\n")
    assert capsys.readouterr().out == "x\n"
    target = tmp_path / "empty.txt"
    target.write_text("previous contents", encoding="utf-8")
    emit("", out=target)
    assert target.read_bytes() == b""
    assert capsys.readouterr().out == ""


def test_scaffold_dry_run_output(capsys, tmp_path):
    (tmp_path / "Makefile").touch()
    assert main(["scaffold", str(tmp_path), "--dry-run"]) == 0
    output = capsys.readouterr().out
    assert _one_newline(output)
    assert "\n\n" not in output


def test_module_entrypoint_json_output_newline():
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    result = subprocess.run(
        [sys.executable, "-m", "qnx_portcheck", "scan", str(EXAMPLE), "--format", "json",
         "--fail-on", "never"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=True,
    )
    assert _one_newline(result.stdout)
    json.loads(result.stdout)
