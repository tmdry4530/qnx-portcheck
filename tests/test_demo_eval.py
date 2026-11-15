import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demo"))
import build_assets

FIXTURE = ROOT / "tests/fixtures/eval/RESULTS.fixture.md"


def test_parse_and_apply_fixture():
    ev, reason = build_assets.load_eval(FIXTURE)
    assert reason == ""
    assert ev == {
        "label": "TEST-FIXTURE", "projects": 33, "scanner": "qnx-portcheck/0.1.0",
        "scanner_commit": "0123456789abcdef0123456789abcdef01234567", "date": "2026-11-14T12:34:56+09:00",
        "recall_source": "0.123", "recall_source_num": 12, "recall_source_den": 97,
        "recall_source_nontest": "0.234", "recall_source_nontest_num": 23, "recall_source_nontest_den": 98,
        "recall_build": "0.345", "recall_build_num": 34, "recall_build_den": 99,
        "precision": "0.456", "precision_num": 45, "precision_den": 100,
        "precision_in_patched_files": "0.567", "precision_in_patched_files_num": 56, "precision_in_patched_files_den": 101,
    }
    source = next(s for s in build_assets.load_scenes() if s["id"] == "05")
    filled = build_assets.apply_eval(source, ev)
    text = " ".join(filled["narration"])
    assert "0.123" in text and "0.456" in text and "[EVAL_NUMBERS]" not in text
    assert build_assets.HONESTY in text
    assert "12/97" in filled["card_text"] and "56/101" in filled["card_text"]


def test_invalid_runs_and_inputs(tmp_path):
    result, reason = build_assets.load_eval(ROOT / "tests/fixtures/eval/RESULTS.fakescan.md")
    assert result is None and reason
    bad = FIXTURE.read_text().replace("0.123 (12/97)", "— (12/97)")
    path = tmp_path / "dash.md"; path.write_text(bad)
    result, reason = build_assets.load_eval(path)
    assert result is None and reason
    path.write_text("malformed")
    result, reason = build_assets.load_eval(path)
    assert result is None and reason
    result, reason = build_assets.load_eval(tmp_path / "missing")
    assert result is None and reason == "missing"


def test_subs_eval_and_fallback(tmp_path):
    missing = tmp_path / "missing.md"
    out = tmp_path / "missing"
    proc = subprocess.run([sys.executable, str(ROOT / "demo/build_assets.py"), "subs", "--out", str(out), "--eval", str(missing)], capture_output=True, text=True)
    assert proc.returncode == 0 and "WARNING: eval numbers not filled" in proc.stderr
    assert (out / "eval_status.txt").read_text().startswith("placeholder")
    assert "[EVAL_NUMBERS]" in (out / "demo.srt").read_text()
    out = tmp_path / "filled"
    subprocess.run([sys.executable, str(ROOT / "demo/build_assets.py"), "subs", "--out", str(out), "--eval", str(FIXTURE)], check=True, capture_output=True, text=True)
    srt = (out / "demo.srt").read_text()
    assert (out / "eval_status.txt").read_text().strip() == "filled"
    assert "0.123" in srt and "[EVAL_NUMBERS]" not in srt
    parsed = build_assets.parse_srt(srt)
    assert parsed and all(a < b for a, b, _ in parsed)


def test_card_text_eval_and_fallback(tmp_path):
    filled = tmp_path / "filled.txt"
    subprocess.run([sys.executable, str(ROOT / "demo/build_assets.py"), "card-text", "--scene", "05", "--out", str(filled), "--eval", str(FIXTURE)], check=True, capture_output=True, text=True)
    assert "0.123" in filled.read_text() and "[EVAL_NUMBERS]" not in filled.read_text()
    missing = tmp_path / "missing.txt"
    proc = subprocess.run([sys.executable, str(ROOT / "demo/build_assets.py"), "card-text", "--scene", "05", "--out", str(missing), "--eval", str(tmp_path / "absent")], capture_output=True, text=True)
    assert proc.returncode == 0 and "WARNING" in proc.stderr and "[EVAL_NUMBERS]" in missing.read_text()


def test_worst_case_budget():
    assert build_assets.check() == 0
