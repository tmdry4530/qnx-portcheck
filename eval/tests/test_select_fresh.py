"""Network-free tests for fresh candidate helper rules."""
import importlib.util
from pathlib import Path
import subprocess


SCRIPT = Path(__file__).parents[1] / "tools" / "select_fresh.py"
spec = importlib.util.spec_from_file_location("select_fresh", SCRIPT)
fresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fresh)


def test_source_qualification_and_file_statuses():
    files = [
        {"filename": "src/a.c", "status": "modified"},
        {"filename": "src/b.C", "status": "removed"},
        {"filename": "src/c.cpp", "status": "renamed", "changes": 2},
        {"filename": "src/d.h", "status": "renamed", "changes": 0},
        {"filename": "src/e.rs", "status": "modified"},
        {"filename": "src/f.cc", "status": "added"},
    ]
    assert fresh.scorable_files(files) == ["src/a.c", "src/b.C", "src/c.cpp"]


def test_base_ref_order_and_unprefixed_branch():
    assert fresh.base_refs("qnx_v2.1", "thing", "main") == ["v2.1", "vv2.1", "2.1", "release-v2.1", "thing-v2.1", "main"]
    assert fresh.base_refs("main", "thing", "upstream") == ["upstream"]


def test_gh_api_decodes_paginated_concatenated_arrays(monkeypatch):
    class Result:
        stdout = '[{"name":"a"}]\n[{"name":"b"}]'

    seen = {}

    def run(command, **kwargs):
        seen["command"] = command
        return Result()

    monkeypatch.setattr(fresh.subprocess, "run", run)
    assert fresh.gh_api("orgs/example/repos", paginate=True) == [{"name": "a"}, {"name": "b"}]
    assert seen["command"] == ["gh", "api", "--paginate", "orgs/example/repos"]


def test_yaml_snippet_key_order_and_note_truncation():
    row = {
        "name": "demo", "qnx_repo": "https://github.com/qnx-ports/demo", "qnx_branch": "qnx-main",
        "qnx_head_sha": "a" * 40, "upstream": "https://github.com/example/demo",
        "upstream_base_ref": "main", "upstream_base_sha": "b" * 40, "compare_status": "ahead",
        "ahead_by": 1, "behind_by": 0, "compare_files": 1,
        "ahead_commits": [{"subject": "x" * 400}],
    }
    text = fresh.yaml_snippet([row])
    assert text.index("name:") < text.index("qnx_repo:") < text.index("extraction:") < text.index("note:") < text.index("split:")
    assert '    note: "' + ("QNX commits: " + "x" * 400)[:300] + '"' in text
    assert text.endswith("    split: fresh\n")


def _candidate(monkeypatch, gh, target=5, rejected=None):
    monkeypatch.setattr(fresh.run_eval, "load_projects", lambda _path: [])
    return fresh.enumerate_candidates(target, rejected or {}, gh=gh)


def _metadata(name="demo"):
    return {"name": name, "default_branch": "qnx-v1", "parent": {
        "full_name": "up/demo", "size": 10, "default_branch": "main"}}


def test_missing_tag_then_default_diverged_skips_with_detail(monkeypatch):
    paths = []

    def gh(path, paginate=False):
        if paginate:
            return [{"name": "demo"}]
        if "/branches/" in path:
            return {"commit": {"sha": "h" * 40}}
        if "/compare/" in path:
            paths.append(path)
            if "/compare/main..." not in path:
                raise subprocess.CalledProcessError(1, ["gh"])
            if "/compare/main..." in path:
                return {"status": "diverged", "ahead_by": 0}
            raise AssertionError(path)
        return _metadata()

    selected, skipped, remaining, names = _candidate(monkeypatch, gh)
    assert not selected and remaining == 0 and names == ["demo"]
    assert "fails verifiable merge-base criterion (ahead_by 0)" in skipped[0]["reason"]


def test_contained_ahead_commit_is_skipped_with_sha(monkeypatch):
    sha = "abcdef1234567890"

    def gh(path, paginate=False):
        if paginate: return [{"name": "demo"}]
        if "/branches/" in path: return {"commit": {"sha": "h" * 40}}
        if "/compare/" in path:
            if "...qnx-ports:" in path:
                return {"status": "ahead", "behind_by": 0, "ahead_by": 1,
                        "merge_base_commit": {"sha": "b" * 40}, "files": [{"filename": "x.c", "status": "modified"}],
                        "commits": [{"sha": sha, "commit": {"message": "change"}}]}
            return {"status": "identical"}
        return _metadata()

    selected, skipped, *_ = _candidate(monkeypatch, gh)
    assert not selected
    assert skipped[0]["reason"] == "ahead commit abcdef12 is contained in upstream"


def test_selection_stops_at_target_and_counts_unexamined(monkeypatch):
    calls = []
    def gh(path, paginate=False):
        if paginate: return [{"name": n} for n in ["a", "b", "c"]]
        calls.append(path)
        if "/branches/" in path: return {"commit": {"sha": "h" * 40}}
        if "/compare/" in path:
            return {"status": "ahead", "behind_by": 0, "ahead_by": 1,
                    "merge_base_commit": {"sha": "b" * 40}, "files": [{"filename": "x.c", "status": "modified"}],
                    "commits": [{"sha": "a" * 40, "commit": {"message": "change"}}]}
        return _metadata(path.split("/")[2])
    selected, skipped, remaining, names = _candidate(monkeypatch, gh, target=1)
    assert [r["name"] for r in selected] == ["a"]
    assert remaining == 2 and names == ["a", "b", "c"]
    assert not any("/repos/qnx-ports/b/" in c or "/repos/qnx-ports/c/" in c for c in calls)


def test_manual_reject_skips_candidate(monkeypatch):
    def gh(path, paginate=False):
        if paginate: return [{"name": "demo"}]
        if "/branches/" in path: return {"commit": {"sha": "h" * 40}}
        if "/compare/" in path:
            if "...qnx-ports:" in path:
                return {"status": "ahead", "behind_by": 0, "ahead_by": 1,
                        "merge_base_commit": {"sha": "b" * 40}, "files": [{"filename": "x.c", "status": "modified"}],
                        "commits": [{"sha": "a" * 40, "commit": {"message": "change"}}]}
            return {"status": "ahead"}
        return _metadata()
    selected, skipped, *_ = _candidate(monkeypatch, gh, rejected={"demo": "duplicate"})
    assert not selected
    assert skipped[0]["reason"] == "manual rejection: duplicate"
