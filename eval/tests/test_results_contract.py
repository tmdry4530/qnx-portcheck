"""Contract checks between eval summary rendering and demo asset parsing."""

import sys
from pathlib import Path

import pytest
import run_eval


ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "demo"
if not (DEMO / "build_assets.py").exists():
    pytest.skip("demo/build_assets.py is missing", allow_module_level=True)
sys.path.insert(0, str(DEMO))
import build_assets


def _summary(label="REAL"):
    projects = []
    for name, source_line, build_line, split in (("alpha", 10, 20, "tune"), ("beta", 30, 40, "holdout"), ("gamma", 50, 60, "fresh")):
        sites = [
            run_eval.Site(f"{name}.c", "source", False, "modify", source_line, 1, source_line, 1, [source_line]),
            run_eval.Site(f"{name}.cmake", "build", False, "modify", build_line, 1, build_line, 1, [build_line]),
        ]
        findings = [
            {"file": f"{name}.c", "line": source_line},
            {"file": f"{name}.cmake", "line": build_line},
            {"file": f"{name}_noise.c", "line": 1},
        ]
        metrics = run_eval.compute_metrics(
            sites, findings, run_eval.match_findings(findings, sites, 0), {f"{name}.c"}
        )
        projects.append({"status": "ok", "name": name, "split": split, "metrics": metrics})
    return {
        "run_config": {
            "label": label,
            "scanner": "qnx-portcheck/0.1.0",
            "scanner_source_commit": "abc1234",
            "date_kst": "2026-11-15",
            "projects_count": 3,
        },
        "splits": {"tune": ["alpha"], "holdout": ["beta"], "fresh": ["gamma"]},
        "projects": projects,
        "aggregate": {**run_eval.aggregate(projects), "by_split": {split: run_eval.aggregate([p for p in projects if p["split"] == split]) for split in ("tune", "holdout", "fresh")}},
    }


def test_rendered_real_summary_is_accepted_and_preserves_micro_values(tmp_path):
    summary = _summary()
    path = tmp_path / "RESULTS.md"
    path.write_text(run_eval.render_summary_md(summary), encoding="utf-8")

    parsed, reason = build_assets.load_eval(path)

    assert reason == ""
    assert parsed is not None
    micro = summary["aggregate"]["by_split"]["fresh"]["micro"]
    expected = {
        "recall_source": ("sites_hit_by_category", "source", "sites_by_category", "source"),
        "recall_source_nontest": ("sites_hit_source_nontest", None, "sites_source_nontest", None),
        "recall_build": ("sites_hit_by_category", "build", "sites_by_category", "build"),
        "precision": ("findings_tp", None, "findings_total", None),
        "precision_in_patched_files": (
            "findings_tp_in_patched_files", None, "findings_in_patched_files", None
        ),
    }
    for metric, (num_key, num_subkey, den_key, den_subkey) in expected.items():
        numerator = micro[num_key][num_subkey] if num_subkey else micro[num_key]
        denominator = micro[den_key][den_subkey] if den_subkey else micro[den_key]
        assert parsed[metric] == f"{micro[metric]:.3f}"
        assert parsed[f"{metric}_num"] == numerator
        assert parsed[f"{metric}_den"] == denominator


def test_rendered_fake_summary_is_rejected(tmp_path):
    path = tmp_path / "FAKE-RESULTS.md"
    path.write_text(run_eval.render_summary_md(_summary("FAKE-SCAN")), encoding="utf-8")

    parsed, reason = build_assets.load_eval(path)

    assert parsed is None
    assert reason == "FAKE run rejected"


def test_committed_results_is_a_real_sufficiently_sized_run():
    path = ROOT / "eval" / "RESULTS.md"
    if not path.exists():
        pytest.skip("eval/RESULTS.md is missing")

    parsed, reason = build_assets.load_eval(path)

    assert reason == ""
    assert parsed is not None
    assert "FAKE" not in parsed["label"].upper()
    assert parsed["scanner"].startswith("qnx-portcheck")
    assert parsed["projects"] >= 15
    rendered = path.read_text()
    fresh = next(line for line in rendered.splitlines() if line.startswith("Split fresh "))
    assert parsed["recall_source"] == fresh.split("source-site recall ", 1)[1].split()[0]
