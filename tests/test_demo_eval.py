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
        "label": "TEST-FIXTURE", "projects": 15, "scanner": "qnx-portcheck/0.1.0",
        "scanner_commit": "0123456789abcdef0123456789abcdef01234567", "date": "2026-11-14T12:34:56+09:00",
        "recall_source": "0.123", "recall_source_num": 12, "recall_source_den": 97,
        "recall_source_nontest": "0.234", "recall_source_nontest_num": 23, "recall_source_nontest_den": 98,
        "recall_build": "0.345", "recall_build_num": 34, "recall_build_den": 99,
        "precision": "0.456", "precision_num": 45, "precision_den": 100,
        "precision_in_patched_files": "0.567", "precision_in_patched_files_num": 56, "precision_in_patched_files_den": 101,
        "tune_projects": 17, "tune_recall_source": "0.111", "tune_recall_source_num": 11, "tune_recall_source_den": 99,
        "tune_recall_source_nontest": "0.112", "tune_recall_source_nontest_num": 12, "tune_recall_source_nontest_den": 99,
        "tune_recall_build": "0.113", "tune_recall_build_num": 13, "tune_recall_build_den": 99,
        "tune_precision": "0.114", "tune_precision_num": 14, "tune_precision_den": 99,
        "tune_precision_in_patched_files": "0.115", "tune_precision_in_patched_files_num": 15, "tune_precision_in_patched_files_den": 99,
        "holdout_projects": 16, "holdout_recall_source": "0.221", "holdout_recall_source_num": 21, "holdout_recall_source_den": 99,
        "holdout_recall_source_nontest": "0.222", "holdout_recall_source_nontest_num": 22, "holdout_recall_source_nontest_den": 99,
        "holdout_recall_build": "0.223", "holdout_recall_build_num": 23, "holdout_recall_build_den": 99,
        "holdout_precision": "0.224", "holdout_precision_num": 24, "holdout_precision_den": 99,
        "holdout_precision_in_patched_files": "0.225", "holdout_precision_in_patched_files_num": 25, "holdout_precision_in_patched_files_den": 99,
    }
    assert ev["recall_source"] != "0.999"
    source = next(s for s in build_assets.load_scenes() if s["id"] == "05")
    filled = build_assets.apply_eval(source, ev)
    text = " ".join(filled["narration"])
    assert "0.123" in text and "0.456" in text and "[EVAL_NUMBERS]" not in text
    assert build_assets.HONESTY in text
    assert "12/97" in filled["card_text"] and "56/101" in filled["card_text"]
    assert "0.111" in filled["card_text"] and "0.221" in filled["card_text"]
    assert "holdout was seen during tuning" in filled["card_text"]


def test_invalid_runs_and_inputs(tmp_path):
    result, reason = build_assets.load_eval(ROOT / "tests/fixtures/eval/RESULTS.fakescan.md")
    assert result is None and reason
    bad = FIXTURE.read_text().replace("Split fresh (micro, 15 projects): source-site recall 0.123", "Split fresh (micro, 15 projects): source-site recall —")
    path = tmp_path / "dash.md"; path.write_text(bad)
    result, reason = build_assets.load_eval(path)
    assert result is None and reason
    valid_overall_dash = FIXTURE.read_text().replace("Overall (micro): source-site recall 0.999", "Overall (micro): source-site recall —")
    path.write_text(valid_overall_dash)
    result, reason = build_assets.load_eval(path)
    assert reason == "" and result["recall_source"] == "0.123"
    path.write_text("malformed")
    result, reason = build_assets.load_eval(path)
    assert result is None and reason
    result, reason = build_assets.load_eval(tmp_path / "missing")
    assert result is None and reason == "missing"
    overall_only = "\n".join(line for line in FIXTURE.read_text().splitlines() if not line.startswith("Split "))
    path.write_text(overall_only)
    result, reason = build_assets.load_eval(path)
    assert result is None and "Split fresh" in reason


def test_committed_results_uses_fresh_split_when_present():
    path = ROOT / "eval/RESULTS.md"
    if not path.exists():
        return
    text = path.read_text()
    fresh = next(line for line in text.splitlines() if line.startswith("Split fresh (micro"))
    expected = fresh.split("source-site recall ", 1)[1].split()[0]
    ev, reason = build_assets.load_eval(path)
    assert reason == "" and ev["recall_source"] == expected


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
    headline = filled.with_name("filled-headline.txt").read_text()
    secondary = filled.with_name("filled-secondary.txt").read_text()
    assert "Fresh split" in headline and "12/97" in headline and "0.999" not in headline
    assert "0.111" in secondary and "0.221" in secondary and "holdout was seen during tuning" in secondary
    missing = tmp_path / "missing.txt"
    proc = subprocess.run([sys.executable, str(ROOT / "demo/build_assets.py"), "card-text", "--scene", "05", "--out", str(missing), "--eval", str(tmp_path / "absent")], capture_output=True, text=True)
    assert proc.returncode == 0 and "WARNING" in proc.stderr and "[EVAL_NUMBERS]" in missing.read_text()


def test_worst_case_budget():
    assert build_assets.check() == 0
