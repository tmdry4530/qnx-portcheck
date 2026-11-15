import json
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest
import run_eval as ev


@pytest.mark.parametrize(
    "path,expected",
    [
        ("a.c", "source"),
        ("a.C", "source"),
        ("x/file.HPP", "source"),
        ("CMakeLists.txt", "build"),
        ("foo.cmake", "build"),
        ("README.md", "other"),
        ("Makefile", "build"),
    ],
)
def test_classify(path, expected):
    assert ev.classify_path(path) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("src/tests/a.c", True),
        ("testing/foo.cpp", True),
        ("foo_test.c", True),
        ("test_thing.py", True),
        ("foo-test.cc", True),
        ("src/tester.c", False),
    ],
)
def test_test_paths(path, expected):
    assert ev.is_test_path(path) is expected


def parse(diff):
    return ev.parse_unified_diff(diff)


def test_diff_multi_hunk_and_omitted_count():
    p = parse(
        "diff --git a/a.c b/a.c\n--- a/a.c\n+++ b/a.c\n@@ -2 +2 @@\n-x\n+y\n@@ -9,2 +9,3 @@\n-a\n-b\n+c\n+d\n+e\n"
    )[0]
    assert p.status == "modified" and [
        (h.old_start, h.old_count, h.new_start, h.new_count) for h in p.hunks
    ] == [(2, 1, 2, 1), (9, 2, 9, 3)]


def test_diff_edge_statuses_and_paths():
    cases = [
        ("diff --git a/f.c b/f.c\n--- a/f.c\n+++ b/f.c\n@@ -0,0 +1 @@\n+x\n", "modified", (0, 0)),
        ("diff --git a/f.c b/f.c\n--- a/f.c\n+++ b/f.c\n@@ -4 +3,0 @@\n-x\n", "modified", (4, 1)),
        (
            "diff --git a/n.c b/n.c\nnew file mode 100644\n--- /dev/null\n+++ b/n.c\n@@ -0,0 +1 @@\n+x\n",
            "added",
            (0, 0),
        ),
        ("diff --git a/d.c b/d.c\ndeleted file mode 100644\n--- a/d.c\n+++ /dev/null\n", "deleted", None),
        (
            "diff --git a/old.c b/new.c\nsimilarity index 90%\nrename from old.c\nrename to new.c\n",
            "renamed",
            None,
        ),
        ("diff --git a/a.bin b/a.bin\nBinary files a/a.bin and b/a.bin differ\n", "binary", None),
        ("diff --git a/sub b/sub\nindex 111..222 160000\n--- a/sub\n+++ b/sub\n", "submodule", None),
        ("diff --git a/m.c b/m.c\nold mode 100644\nnew mode 100755\n", "modified", None),
        (
            "diff --git a/a file.c b/a file.c\n--- a/a file.c\n+++ b/a file.c\n@@ -1 +1 @@\n-x\n+y\n\\ No newline at end of file\n",
            "modified",
            None,
        ),
    ]
    for text, status, _ in cases:
        p = parse(text)[0]
        assert p.status == status
    assert parse(cases[-1][0])[0].old_path == "a file.c"
    assert parse(cases[4][0])[0].old_path == "old.c"
    assert not parse(cases[-2][0])[0].hunks


def test_build_sites_and_matching():
    patches = [
        ev.FilePatch("src/a.c", "src/a.c", "modified", [ev.Hunk(4, 2, 4, 1), ev.Hunk(10, 0, 11, 2)]),
        ev.FilePatch(None, "new.cpp", "added", [ev.Hunk(0, 0, 1, 3)]),
    ]
    sites = ev.build_sites(patches)
    out = ev.build_out_of_scope(patches)
    assert sites[0].target_lines == [4, 5] and sites[0].kind == "modify"
    assert sites[1].target_lines == [10, 11] and sites[1].kind == "insert"
    assert out["new_files"] == [{"path": "new.cpp", "category": "source", "added_lines": 3}]
    findings = [
        {"file": "./src/a.c", "line": 8},
        {"file": "src/a.c", "line": 12},
        {"file": "else.c", "line": 4},
        {"file": "src/a.c", "line": None},
        {"file": "src/a.c", "line": 0},
    ]
    m = ev.match_findings(findings, sites, 3)
    assert m["finding_sites"] == [[0, 1], [1], [], [], []]
    assert ev.match_findings([{"file": "src/a.c", "line": 14}], sites, 3)["finding_sites"] == [[1]]
    assert ev.match_findings([{"file": "src/a.c", "line": 15}], sites, 3)["finding_sites"] == [[]]


def test_build_sites_merge_gap():
    adjacent = ev.FilePatch("a.c", "a.c", "modified", [ev.Hunk(256, 0, 257, 1), ev.Hunk(257, 0, 259, 1)])
    distant = ev.FilePatch("a.c", "a.c", "modified", [ev.Hunk(300, 0, 301, 1)])
    other_file = ev.FilePatch("b.c", "b.c", "modified", [ev.Hunk(258, 0, 259, 1)])
    merged = ev.build_sites([adjacent, distant], merge_gap=3)
    assert len(merged) == 2
    assert merged[0].target_lines == [256, 257, 258] and merged[0].hunks == 2
    non_touching = ev.FilePatch("a.c", "a.c", "modified", [ev.Hunk(256, 0, 257, 1), ev.Hunk(258, 0, 260, 1)])
    assert len(ev.build_sites([non_touching], merge_gap=0)) == 2
    assert len(ev.build_sites([adjacent, other_file], merge_gap=3)) == 2


def test_metrics_and_zero_denominators():
    sites = [
        ev.Site("a.c", "source", False, "modify", 1, 1, 1, 1, [1]),
        ev.Site("x.cmake", "build", False, "modify", 2, 1, 2, 1, [2]),
        ev.Site("readme", "other", False, "modify", 3, 1, 3, 1, [3]),
    ]
    fs = [
        {"file": "a.c", "line": 1},
        {"file": "a.c", "line": 20},
        {"file": "x.cmake", "line": 2},
        {"file": "z.c", "line": 1},
    ]
    m = ev.match_findings(fs, sites, 0)
    got = ev.compute_metrics(sites, fs, m, {"a.c", "x.cmake"})
    assert got["sites_hit_by_category"] == {"source": 1, "build": 1, "other": 0}
    assert (
        got["recall_source"],
        got["recall_build"],
        got["precision"],
        got["precision_in_patched_files"],
    ) == (1.0, 1.0, 0.5, 0.6667)
    zero = ev.compute_metrics([], [], {"site_findings": [], "finding_sites": []}, set())
    assert zero["recall_source"] is None and zero["precision"] is None


def test_aggregate_micro_macro_skips_errors():
    def row(s, hit, prec, status="ok"):
        return {
            "status": status,
            "metrics": {
                "sites_by_category": {"source": s, "build": 0, "other": 0},
                "sites_hit_by_category": {"source": hit, "build": 0, "other": 0},
                "findings_total": 1,
                "findings_tp": int(prec),
                "findings_by_category": {"source": 1, "build": 0, "other": 0},
                "recall_source": hit / s if s else None,
                "recall_build": None,
                "recall_in_scope": hit / s if s else None,
                "precision": prec,
                "precision_in_patched_files": prec,
            },
        }

    a = ev.aggregate([row(1, 1, 1), row(3, 0, 0), row(9, 9, 1, "error")])
    assert a["micro"]["recall_source"] == 0.25
    assert a["macro"]["recall_source"] == {"mean": 0.5, "n": 2}
    assert a["counts"] == {"ok_projects": 2, "error_projects": 1}


def test_projects_loaders_and_validation():
    path = Path(__file__).parents[1] / "projects.yaml"
    mini = ev.load_projects(path, False)
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML unavailable")
    assert (
        mini == ev.load_projects(path, True)
        and len(mini) >= 15
        and len({p["name"] for p in mini}) == len(mini)
    )
    assert all(
        ev.SHA_RE.fullmatch(p["upstream_base_sha"]) and ev.SHA_RE.fullmatch(p["qnx_head_sha"]) for p in mini
    )
    with pytest.raises(ValueError, match="40-character"):
        ev.validate_project(
            {
                "name": "x",
                "upstream": "u",
                "upstream_base_sha": "x",
                "qnx_repo": "q",
                "qnx_head_sha": "0" * 40,
                "extraction": "git-diff-fork",
            }
        )
    with pytest.raises(ValueError, match="missing required"):
        ev.validate_project({})
    p = mini[0]
    dup = Path(__file__).parent / "dup.yaml"
    dup.write_text(
        'projects:\n  - name: a\n    upstream: u\n    upstream_base_sha: "'
        + "0" * 40
        + '"\n    qnx_repo: q\n    qnx_head_sha: "'
        + "1" * 40
        + '"\n    extraction: git-diff-fork\n  - name: a\n    upstream: u\n    upstream_base_sha: "'
        + "0" * 40
        + '"\n    qnx_repo: q\n    qnx_head_sha: "'
        + "1" * 40
        + '"\n    extraction: git-diff-fork\n'
    )
    with pytest.raises(ValueError, match="duplicate"):
        ev.load_projects(dup, False)
    dup.unlink()


def test_scan_validation_and_fake_scan(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "a.c").write_text("int x;\nepoll_create(1);\n")
    cp = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parents[1] / "fake_scan.py"),
            "scan",
            str(root),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    obj = json.loads(cp.stdout)
    fs = ev.validate_scan_output(obj)
    assert obj["tool"] == "fake-scan" and fs[0]["line"] == 2 and fs[0]["col"] == 1
    for bad in ({}, {"tool": "x", "version": "v", "root": "r", "findings": [{"line": 0}]}):
        with pytest.raises(ValueError):
            ev.validate_scan_output(bad)


def test_summary_warning():
    summary = {"run_config": {"label": "FAKE-SCAN", "projects_count": 0}}
    assert "NOT qnx-portcheck" in ev.render_summary_md(summary)
    summary["run_config"]["label"] = "REAL"
    assert "NOT qnx-portcheck" not in ev.render_summary_md(summary)


def test_out_of_scope_rename_empty_delete_and_mode_only():
    patches = [
        ev.FilePatch("old.c", "new.c", "renamed"),
        ev.FilePatch("empty.c", None, "deleted"),
        ev.FilePatch("mode.c", "mode.c", "modified", old_mode="100644", new_mode="100755"),
    ]
    out = ev.build_out_of_scope(patches)
    assert out["rename_only"] == [{"old_path": "old.c", "new_path": "new.c"}]
    assert out["deleted_empty"] == ["empty.c"]
    assert out["mode_only"] == ["mode.c"]


def test_metrics_patched_file_counts_and_source_nontest():
    sites = [
        ev.Site("src/a.c", "source", False, "modify", 1, 1, 1, 1, [1]),
        ev.Site("tests/b.c", "source", True, "modify", 2, 1, 2, 1, [2]),
    ]
    findings = [
        {"file": "src/a.c", "line": 1},
        {"file": "tests/b.c", "line": 2},
        {"file": "other.c", "line": 8},
    ]
    match = ev.match_findings(findings, sites, 0)
    metrics = ev.compute_metrics(sites, findings, match, {"src/a.c"})
    assert metrics["sites_hit_source_nontest"] == 1
    assert metrics["findings_in_patched_files"] == 1
    assert metrics["findings_tp_in_patched_files"] == 1


def test_aggregate_micro_source_nontest_and_patched_precision():
    metrics = {
        "sites_by_category": {"source": 3, "build": 1, "other": 0},
        "sites_hit_by_category": {"source": 2, "build": 1, "other": 0},
        "sites_source_nontest": 2,
        "sites_hit_source_nontest": 1,
        "findings_total": 4,
        "findings_tp": 3,
        "findings_by_category": {"source": 3, "build": 1, "other": 0},
        "findings_in_patched_files": 2,
        "findings_tp_in_patched_files": 1,
        "recall_source": 2 / 3,
        "recall_source_nontest": 0.5,
        "recall_build": 1.0,
        "recall_in_scope": 0.75,
        "precision": 0.75,
        "precision_in_patched_files": 0.5,
    }
    agg = ev.aggregate([{"status": "ok", "metrics": metrics}])
    assert agg["micro"]["recall_source_nontest"] == 0.5
    assert agg["micro"]["precision_in_patched_files"] == 0.5
    assert agg["macro"]["recall_source_nontest"] == {"mean": 0.5, "n": 1}


def test_summary_table_rows_have_consistent_columns():
    summary = {
        "run_config": {"label": "REAL"},
        "projects": [
            {
                "name": "sample",
                "upstream_base_sha": "a" * 40,
                "status": "ok",
                "metrics": {
                    "sites_by_category": {"source": 2, "build": 1, "other": 0},
                    "sites_source_nontest": 1,
                    "findings_total": 2,
                    "findings_tp": 1,
                    "recall_source": 0.5,
                    "recall_source_nontest": 1.0,
                    "recall_build": 1.0,
                    "precision": 0.5,
                    "precision_in_patched_files": 1.0,
                },
                "out_of_scope": {},
            }
        ],
        "aggregate": {"micro": {}, "macro": {}},
    }
    table_lines = [line for line in ev.render_summary_md(summary).splitlines() if line.startswith("|")]
    assert len({line.count("|") for line in table_lines}) == 1


def git(cwd, *args, env=None):
    subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def test_end_to_end_local_git(tmp_path, monkeypatch):
    empty = tmp_path / "empty.gitconfig"
    empty.write_text("")
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Harness Test",
            "GIT_AUTHOR_EMAIL": "harness@example.invalid",
            "GIT_COMMITTER_NAME": "Harness Test",
            "GIT_COMMITTER_EMAIL": "harness@example.invalid",
            "GIT_CONFIG_GLOBAL": str(empty),
        }
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    up = tmp_path / "upstream"
    up.mkdir()
    git(up, "init", "-q", env=env)
    (up / "a.c").write_text("#include <sys/epoll.h>\nint main(){ return epoll_create(1); }\n")
    (up / "CMakeLists.txt").write_text("project(example)\n")
    git(up, "add", ".", env=env)
    git(up, "commit", "-qm", "base", env=env)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=up, text=True).strip()
    fork = tmp_path / "fork"
    git(tmp_path, "clone", "-q", str(up), str(fork), env=env)
    (fork / "a.c").write_bytes(
        b"#include <sys/epoll.h>\n/* latin-1: \xf3 */\nint main(){ return epoll_create1(0); }\n"
    )
    (fork / "qnx").mkdir()
    (fork / "qnx/foo.c").write_text("int qnx;\n")
    (fork / "CMakeLists.txt").write_text("project(example)\nset(QNX ON)\n")
    git(fork, "add", ".", env=env)
    git(fork, "commit", "-qm", "port", env=env)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=fork, text=True).strip()
    proj = tmp_path / "projects.yaml"
    proj.write_text(
        f'projects:\n  - name: local\n    qnx_repo: "{fork}"\n    qnx_branch: local\n    qnx_head_sha: "{head}"\n    upstream: "{up}"\n    upstream_base_ref: base\n    upstream_base_sha: "{base}"\n    extraction: git-diff-fork\n    compare_files: 3\n    expected_scope: source\n    verified: true\n'
    )
    evaldir = Path(__file__).parents[1]
    summary = tmp_path / "RESULTS.md"
    code = ev.main(
        [
            "--projects",
            str(proj),
            "--scan-cmd",
            f"{sys.executable} {evaldir/'fake_scan.py'} scan {{path}} --format json",
            "--label",
            "FAKE-SCAN",
            "--work-dir",
            str(tmp_path / "work"),
            "--results-dir",
            str(tmp_path / "results"),
            "--summary",
            str(summary),
        ]
    )
    assert code == 0
    result = json.loads((tmp_path / "results/fake-scan/local.json").read_text())
    assert result["status"] == "ok" and result["metrics"]["recall_source"] == 1.0
    assert result["out_of_scope"]["new_files"][0]["path"] == "qnx/foo.c"
    assert result["out_of_scope"]["build_sites"] == 1
    assert result["window"] == 3 and result["merge_gap"] == 3
    assert b"\xf3" in (tmp_path / "work/local.qnx.diff").read_bytes()
    summary_json = json.loads((tmp_path / "results/fake-scan/summary.json").read_text())
    assert summary_json["run_config"]["window"] == 3
    assert summary_json["run_config"]["merge_gap"] == 3
    assert "NOT qnx-portcheck" in summary.read_text()
