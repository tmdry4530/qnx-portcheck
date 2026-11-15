import json
import os
import re
import subprocess
import sys
from pathlib import Path

import run_eval as ev


def test_display_scan_cmd():
    root = Path(ev.__file__).resolve().parents[1]
    assert (
        ev.display_scan_cmd(
            "/x/wt/.venv/bin/python -m qnx_portcheck scan {path} --format json --fail-on never"
        )
        == "python -m qnx_portcheck scan {path} --format json --fail-on never"
    )
    assert ev.display_scan_cmd("python3 eval/fake_scan.py scan {path} --format json") == (
        "python3 eval/fake_scan.py scan {path} --format json"
    )
    assert (
        ev.display_scan_cmd(f"/usr/bin/python3 {root}/eval/fake_scan.py scan {{path}} --format json")
        == "python eval/fake_scan.py scan {path} --format json"
    )
    assert ev.display_scan_cmd("/opt/bin/qnx-portcheck scan {path}") == "qnx-portcheck scan {path}"
    assert ev.display_scan_cmd("/usr/bin/python3 '/tmp/a b.py' {path}") == "python '<abs>/a b.py' {path}"


def test_sanitize_paths_nested(tmp_path):
    repo = tmp_path / "repo"
    work = repo / "eval" / "work"
    data = {"items": [str(work / "project"), f"at {repo}/eval/run_eval.py", "rule-id R123"]}
    clean = ev.sanitize_paths(data, repo, work)
    assert clean == {"items": ["eval/work/project", "at ./eval/run_eval.py", "rule-id R123"]}
    assert ev.sanitize_paths({"x": str(tmp_path / "other")}, repo, tmp_path / "outside") == {
        "x": "<abs>/other"
    }
    assert ev.sanitize_paths({"x": r"C:\Users\person\work\src"}, repo, work) == {"x": "<abs>/src"}


def _git(cwd, *args, env):
    subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def test_paths_end_to_end_reuse(tmp_path, monkeypatch):
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "T",
            "GIT_AUTHOR_EMAIL": "t@invalid",
            "GIT_COMMITTER_NAME": "T",
            "GIT_COMMITTER_EMAIL": "t@invalid",
            "GIT_CONFIG_GLOBAL": str(tmp_path / "gitconfig"),
        }
    )
    (tmp_path / "gitconfig").write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", env=env)
    (upstream / "a.c").write_text("int f(){ return epoll_create(1); }\n")
    _git(upstream, "add", ".", env=env)
    _git(upstream, "commit", "-qm", "base", env=env)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream, text=True).strip()
    fork = tmp_path / "fork"
    _git(tmp_path, "clone", "-q", str(upstream), str(fork), env=env)
    (fork / "a.c").write_text("int f(){ return epoll_create1(0); }\n")
    _git(fork, "commit", "--allow-empty", "-qm", "port", env=env)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=fork, text=True).strip()
    projects = tmp_path / "projects.yaml"
    projects.write_text(
        f'projects:\n  - name: local\n    qnx_repo: "{fork}"\n    qnx_head_sha: "{head}"\n'
        f'    upstream: "{upstream}"\n    upstream_base_sha: "{base}"\n    extraction: git-diff-fork\n    verified: true\n'
    )
    out = tmp_path / "results"
    summary = tmp_path / "RESULTS.md"
    work = tmp_path / "work"
    cmd = (
        f"{sys.executable} {Path(ev.__file__).resolve().parent / 'fake_scan.py'} scan {{path}} --format json"
    )
    args = [
        "--projects",
        str(projects),
        "--scan-cmd",
        cmd,
        "--label",
        "FAKE-SCAN",
        "--work-dir",
        str(work),
        "--results-dir",
        str(out),
        "--summary",
        str(summary),
    ]
    assert ev.main(args) == 0
    result_path = out / "fake-scan/local.json"
    summary_path = out / "fake-scan/summary.json"
    first = json.loads(result_path.read_text())
    metrics = first["metrics"]
    for artifact in (result_path, summary_path, summary):
        content = artifact.read_text()
        assert str(tmp_path) not in content
        assert not re.search(r"/tmp/|/home/|/workspace/", content)
    assert ev.main(args + ["--require-reuse"]) == 0
    second = json.loads(result_path.read_text())
    run = json.loads(summary_path.read_text())
    assert second["status"] == "ok" and run["run_config"]["reused_projects"] == 1
    assert second["metrics"] == metrics


def test_committed_artifacts_have_no_absolute_paths():
    root = Path(ev.__file__).resolve().parents[1]
    paths = list((root / "eval/results").rglob("*.json"))
    paths.append(root / "eval/RESULTS.md")
    fake = root / "eval/RESULTS-FAKE-SCAN.md"
    if fake.exists():
        paths.append(fake)
    pattern = re.compile(r"(/workspace/|/tmp/|/home/|/root/|/Users/|[A-Za-z]:\\\\)")
    offenders = []
    for path in paths:
        if not path.is_file():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.relative_to(root)}:{line_number}")
    assert not offenders, "absolute paths in committed artifacts:\n" + "\n".join(offenders)
