"""Split assignment and rendering contracts."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import run_eval as ev


def test_assign_splits_is_deterministic_case_sensitive_and_balanced():
    names = ["alpha", "Zeta", "beta", "Alpha", "gamma"]
    projects = [{"name": name} for name in names]
    first = ev.assign_splits(projects)
    assert ev.assign_splits(projects) == first
    assert ev.assign_splits(list(reversed(projects))) == first
    # Python's case-sensitive code-point order places uppercase names first.
    assert sorted(names) == ["Alpha", "Zeta", "alpha", "beta", "gamma"]
    assert [name for name in sorted(names) if first[name] == "tune"] == ["Alpha", "alpha", "gamma"]
    assert [name for name in sorted(names) if first[name] == "holdout"] == ["Zeta", "beta"]
    assert {name for name, split in first.items() if split == "tune"} | {
        name for name, split in first.items() if split == "holdout"
    } == set(names)
    assert not (
        {name for name, split in first.items() if split == "tune"}
        & {name for name, split in first.items() if split == "holdout"}
    )
    assert (
        abs(
            sum(split == "tune" for split in first.values())
            - sum(split == "holdout" for split in first.values())
        )
        <= 1
    )


def test_real_corpus_split_counts():
    projects = ev.load_projects(Path(__file__).parents[1] / "projects.yaml")
    splits = ev.assign_splits(projects)
    originals = [p for p in projects if "split" not in p]
    assert len(projects) == 48
    assert sum(value == "tune" for value in splits.values()) == 17
    assert sum(value == "holdout" for value in splits.values()) == 16
    assert sum(value == "fresh" for value in splits.values()) == 15
    assert {n: splits[n] for n in (p["name"] for p in originals)} == ev.assign_splits(
        [{"name": p["name"]} for p in originals]
    )


def test_fresh_entries_do_not_shift_original_split_and_invalid_explicit_rejected():
    originals = [{"name": "alpha"}, {"name": "gamma"}, {"name": "omega"}]
    original_splits = ev.assign_splits(originals)
    combined = originals + [{"name": "beta", "split": "fresh"}, {"name": "delta", "split": "fresh"}]
    combined_splits = ev.assign_splits(combined)
    assert {p["name"]: combined_splits[p["name"]] for p in originals} == original_splits
    assert combined_splits["beta"] == combined_splits["delta"] == "fresh"
    with pytest.raises(ValueError, match="explicit split"):
        ev.assign_splits([{"name": "bad", "split": "tune"}])


def test_validate_project_rejects_unknown_explicit_split(tmp_path):
    project_file = _corpus(tmp_path)
    project_file.write_text(
        project_file.read_text().replace("    verified: true", "    verified: true\n    split: holdout", 1)
    )
    with pytest.raises(ValueError, match="split must be 'fresh'"):
        ev.load_projects(project_file)


def _git(cwd, *args):
    env = {
        **__import__("os").environ,
        "GIT_AUTHOR_NAME": "Harness Test",
        "GIT_AUTHOR_EMAIL": "harness@example.invalid",
        "GIT_COMMITTER_NAME": "Harness Test",
        "GIT_COMMITTER_EMAIL": "harness@example.invalid",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def _corpus(tmp_path):
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q")
    (upstream / "a.c").write_text("int main(void) { return 0; }\n")
    _git(upstream, "add", ".")
    _git(upstream, "commit", "-qm", "base")
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream, text=True).strip()
    fork = tmp_path / "fork"
    _git(tmp_path, "clone", "-q", str(upstream), str(fork))
    (fork / "a.c").write_text("int main(void) { return 1; }\n")
    _git(fork, "add", ".")
    _git(fork, "commit", "-qm", "port")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=fork, text=True).strip()
    project_file = tmp_path / "projects.yaml"
    entries = []
    for name in ("alpha", "beta", "gamma"):
        entries.append(
            f'  - name: {name}\n    qnx_repo: "{fork}"\n    qnx_branch: local\n'
            f'    qnx_head_sha: "{head}"\n    upstream: "{upstream}"\n'
            f'    upstream_base_ref: base\n    upstream_base_sha: "{base}"\n'
            "    extraction: git-diff-fork\n    verified: true\n"
        )
    project_file.write_text("projects:\n" + "".join(entries))
    return project_file


def _run(tmp_path, projects, extra=(), label="FAKE-SCAN"):
    evaldir = Path(__file__).parents[1]
    return ev.main(
        [
            "--projects",
            str(projects),
            "--scan-cmd",
            f"{sys.executable} {evaldir / 'fake_scan.py'} scan {{path}} --format json",
            "--label",
            label,
            "--work-dir",
            str(tmp_path / "work"),
            "--results-dir",
            str(tmp_path / "results"),
            "--summary",
            str(tmp_path / "RESULTS.md"),
            *extra,
        ]
    )


def test_selection_keeps_split_membership_and_holdout_only(tmp_path):
    projects = _corpus(tmp_path)
    assert _run(tmp_path, projects) == 0
    full = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    beta_split = next(row["split"] for row in full["projects"] if row["name"] == "beta")
    assert _run(tmp_path, projects, ("--only", "beta")) == 0
    only = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    assert only["projects"][0]["split"] == beta_split
    assert _run(tmp_path, projects, ("--split", "holdout")) == 0
    holdout = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    assert [row["name"] for row in holdout["projects"]] == ["beta"]
    assert holdout["run_config"]["split"] == "holdout"


def test_require_reuse_rescores_without_scanning_and_marks_missing(tmp_path):
    projects = _corpus(tmp_path)
    marker = tmp_path / "scanner-called"
    scanner = tmp_path / "scanner.py"
    evaldir = Path(__file__).parents[1]
    scanner.write_text(
        "import pathlib, subprocess, sys\n"
        f"marker=pathlib.Path({str(marker)!r})\n"
        "if marker.exists(): sys.exit(3)\n"
        "marker.write_text('called')\n"
        f"sys.exit(subprocess.call([sys.executable, {str(evaldir / 'fake_scan.py')!r}, 'scan', sys.argv[1], '--format', 'json']))\n"
    )
    scan_cmd = f"{sys.executable} {scanner} {{path}}"
    args = [
        "--projects",
        str(projects),
        "--scan-cmd",
        scan_cmd,
        "--label",
        "FAKE-SCAN",
        "--work-dir",
        str(tmp_path / "work"),
        "--results-dir",
        str(tmp_path / "results"),
        "--summary",
        str(tmp_path / "RESULTS.md"),
    ]
    assert ev.main(args + ["--only", "alpha"]) == 0
    before = json.loads((tmp_path / "results/fake-scan/alpha.json").read_text())
    marker.unlink()
    assert ev.main(args + ["--only", "alpha", "--require-reuse"]) == 0
    after = json.loads((tmp_path / "results/fake-scan/alpha.json").read_text())
    assert after["metrics"] == before["metrics"]
    assert not marker.exists()
    assert "Scan results generated (KST):" in (tmp_path / "RESULTS.md").read_text()
    assert ev.main(args + ["--only", "beta", "--require-reuse"]) == 2
    missing = json.loads((tmp_path / "results/fake-scan/beta.json").read_text())
    assert missing["status"] == "error" and missing["error_kind"] == "not-reused"
    assert not (tmp_path / "work/beta").exists()


def test_split_markdown_lines_match_aggregates_and_demo_contract(tmp_path):
    demo = Path(__file__).parents[2] / "demo" / "build_assets.py"
    if not demo.exists():
        pytest.skip("demo/build_assets.py is missing")
    sys.path.insert(0, str(demo.parent))
    import build_assets

    projects = []
    for name, split, line in (("alpha", "tune", 10), ("beta", "holdout", 20)):
        sites = [
            ev.Site(f"{name}.c", "source", False, "modify", line, 1, line, 1, [line]),
            ev.Site(f"{name}.cmake", "build", False, "modify", line + 1, 1, line + 1, 1, [line + 1]),
        ]
        findings = [{"file": f"{name}.c", "line": line}, {"file": f"{name}.cmake", "line": line + 1}]
        metrics = ev.compute_metrics(
            sites, findings, ev.match_findings(findings, sites, 0), {f"{name}.c", f"{name}.cmake"}
        )
        projects.append({"status": "ok", "name": name, "split": split, "metrics": metrics})
    aggregate = ev.aggregate(projects)
    aggregate["by_split"] = {
        split: ev.aggregate([p for p in projects if p["split"] == split])
        for split in ("tune", "holdout", "fresh")
    }
    summary = {
        "run_config": {
            "label": "REAL",
            "date_kst": "2026-11-15",
            "scanner": "qnx-portcheck/1",
            "scanner_source_commit": "abc1234",
            "projects_count": 2,
            "generated_at_range": "x to y",
        },
        "splits": {"rule": ev.SPLIT_RULE, "tune": ["alpha"], "holdout": ["beta"], "fresh": []},
        "projects": projects,
        "aggregate": aggregate,
    }
    rendered = ev.render_summary_md(summary)
    lines = rendered.splitlines()
    assert next(line for line in lines if line.startswith("Split tune (micro")).startswith(
        "Split tune (micro"
    )
    assert next(line for line in lines if line.startswith("Split holdout (seen during tuning)")).startswith(
        "Split holdout (seen during tuning)"
    )
    tune_line = next(line for line in lines if line.startswith("Split tune (micro"))
    tune_micro = aggregate["by_split"]["tune"]["micro"]
    assert f"source-site recall {tune_micro['recall_source']:.3f} " in tune_line
    assert (
        f"({tune_micro['sites_hit_by_category']['source']}/{tune_micro['sites_by_category']['source']})"
        in tune_line
    )
    path = tmp_path / "RESULTS.md"
    path.write_text(rendered)
    parsed, reason = build_assets.load_eval(path)
    assert reason == "" and parsed["recall_source"] == f"{aggregate['micro']['recall_source']:.3f}"


def test_fresh_only_and_overall_excludes_fresh_end_to_end(tmp_path):
    projects = _corpus(tmp_path)
    content = projects.read_text()
    # beta and gamma are marked fresh, with beta sorting between original names.
    content = content.replace("  - name: beta\n", "  - name: beta\n    split: fresh\n")
    content = content.replace("  - name: gamma\n", "  - name: gamma\n    split: fresh\n")
    projects.write_text(content)

    assert _run(tmp_path, projects, ("--split", "fresh")) == 0
    fresh_summary = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    assert {p["name"] for p in fresh_summary["projects"]} == {"beta", "gamma"}
    for p in fresh_summary["projects"]:
        row = json.loads((tmp_path / f"results/fake-scan/{p['name']}.json").read_text())
        assert row["split"] == "fresh"

    assert _run(tmp_path, projects, ("--only", "alpha,beta")) == 0
    summary = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    alpha = next(p for p in summary["projects"] if p["name"] == "alpha")
    assert summary["aggregate"]["micro"] == ev.aggregate([alpha])["micro"]
    markdown = (tmp_path / "RESULTS.md").read_text()
    assert "- Projects: 1" in markdown
    split_lines = [line for line in markdown.splitlines() if line.startswith("Split ")]
    assert [line.split(" (micro", 1)[0] for line in split_lines] == [
        "Split tune",
        "Split holdout (seen during tuning)",
        "Split fresh",
    ]
    assert "(seen during tuning)" in split_lines[1]
