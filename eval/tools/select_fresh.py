#!/usr/bin/env python3
"""Deterministically select fresh QNX ports using the rules in eval/METHOD.md."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

EVAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL))
import run_eval  # noqa: E402


def gh_api(path: str, paginate: bool = False):
    """Run a read-only GitHub API GET and decode ordinary or concatenated JSON."""
    command = ["gh", "api"] + (["--paginate"] if paginate else []) + [path]
    raw = subprocess.run(command, check=True, capture_output=True, text=True).stdout
    decoder, pos, values = json.JSONDecoder(), 0, []
    while pos < len(raw):
        while pos < len(raw) and raw[pos].isspace():
            pos += 1
        if pos == len(raw):
            break
        value, pos = decoder.raw_decode(raw, pos)
        values.append(value)
    if not paginate:
        if len(values) != 1:
            raise ValueError("expected one JSON value from gh api")
        return values[0]
    flattened = []
    for value in values:
        flattened.extend(value if isinstance(value, list) else [value])
    return flattened


def source_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return suffix in run_eval.SOURCE_EXTS or name.endswith(".C")


def scorable_files(files: list[dict]) -> list[str]:
    found = []
    for f in files:
        status = f.get("status")
        path = f.get("filename", "")
        qualifies = status in {"modified", "removed"} or (
            status == "renamed" and f.get("changes", 0) > 0
        )
        if qualifies and source_path(path):
            found.append(path)
    return found


def base_refs(branch: str, repo: str, upstream_default: str) -> list[str]:
    rest = branch
    for prefix in ("qnx-", "qnx_"):
        if rest.startswith(prefix):
            rest = rest[len(prefix):]
            break
    if rest != branch:
        refs = [rest, "v" + rest, rest[1:] if rest.startswith("v") else rest,
                "release-" + rest, repo + "-" + rest]
    else:
        refs = []
    return refs + [upstream_default]


def compare(path: str, gh=gh_api) -> dict | None:
    try:
        return gh(path)
    except (subprocess.CalledProcessError, ValueError):
        return None


def reject_map(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        name, sep, reason = value.partition(":")
        if not sep or not name or not reason:
            raise ValueError(f"invalid --reject {value!r}; expected NAME:REASON")
        result[name] = reason
    return result


def enumerate_candidates(target: int, rejected: dict[str, str], gh=gh_api):
    """Return selected rows, skipped rows and names remaining after the stop."""
    projects = run_eval.load_projects(EVAL / "projects.yaml")
    original = {p["name"] for p in projects}
    repos = sorted(gh("orgs/qnx-ports/repos", paginate=True), key=lambda r: r["name"])
    selected, skipped = [], []
    names = [r["name"] for r in repos]

    def skip(name, reason):
        skipped.append({"name": name, "reason": reason})

    for index, repo_row in enumerate(repos):
        name = repo_row["name"]
        if len(selected) >= target:
            return selected, skipped, len(repos) - index, names
        if name in original:
            skip(name, "original project")
            continue
        try:
            info = gh(f"repos/qnx-ports/{quote(name, safe='')}")
        except (subprocess.CalledProcessError, ValueError, KeyError):
            skip(name, "repo metadata unavailable")
            continue
        parent = info.get("parent")
        if not parent:
            skip(name, "not a fork")
            continue
        upstream = f"https://github.com/{parent['full_name']}"
        parent_info = parent
        if "size" not in parent_info or "default_branch" not in parent_info:
            try:
                parent_info = gh(f"repos/{quote(parent['full_name'], safe='/')}")
            except (subprocess.CalledProcessError, ValueError, KeyError):
                skip(name, "repo metadata unavailable")
                continue
        if parent_info.get("size", 0) > 500000:
            skip(name, f"upstream larger than 500000 KB (size {parent_info.get('size')})")
            continue
        try:
            branch = info["default_branch"]
            upstream_default = parent_info["default_branch"]
        except (KeyError, TypeError):
            skip(name, "repo metadata unavailable")
            continue
        try:
            qnx_branch = gh(f"repos/qnx-ports/{quote(name, safe='')}/branches/{quote(branch, safe='')}")
        except (subprocess.CalledProcessError, ValueError, KeyError):
            skip(name, "repo metadata unavailable")
            continue
        head_sha = qnx_branch["commit"]["sha"]
        chosen = None
        for ref in base_refs(branch, name, upstream_default):
            candidate = compare(f"repos/{quote(parent['full_name'], safe='/')}/compare/{quote(ref, safe='')}...qnx-ports:{quote(branch, safe='')}", gh)
            if candidate is None:
                continue
            if candidate.get("status") == "ahead" and candidate.get("behind_by", 0) == 0:
                chosen = (ref, candidate)
                break
        if chosen is None:
            candidate = compare(f"repos/{quote(parent['full_name'], safe='/')}/compare/{quote(upstream_default, safe='')}...qnx-ports:{quote(branch, safe='')}", gh)
            if candidate is None:
                skip(name, "compare API error against upstream default branch")
                continue
            if candidate.get("status") != "diverged":
                skip(name, f"no qualifying base ref (status {candidate.get('status')}, base ref {upstream_default})")
                continue
            chosen = (upstream_default, candidate)
        base_ref, cmp = chosen
        ahead_by = cmp.get("ahead_by", 0)
        if ahead_by > 50:
            skip(name, f"more than 50 ahead commits (ahead_by {ahead_by})")
            continue
        if not cmp.get("merge_base_commit") or ahead_by < 1 or not cmp.get("files"):
            skip(name, f"fails verifiable merge-base criterion (ahead_by {ahead_by})")
            continue
        ahead_commits = []
        upstream_commit = False
        for commit in cmp.get("commits", []):
            sha = commit["sha"]
            subject = commit.get("commit", {}).get("message", "").splitlines()[0]
            author = (commit.get("author") or {}).get("login") or commit.get("commit", {}).get("author", {}).get("name", "")
            ahead_commits.append({"sha": sha, "subject": subject, "author": author})
            containment = compare(f"repos/{quote(parent['full_name'], safe='/')}/compare/{quote(upstream_default, safe='')}...{sha}", gh)
            if containment is None:
                skip(name, f"could not verify ahead commit {sha[:8]}")
                upstream_commit = None
                break
            status = containment.get("status")
            if status in {"behind", "identical"}:
                upstream_commit = sha
            elif status not in {"ahead", "diverged"}:
                upstream_commit = sha
        if upstream_commit is None:
            continue
        if upstream_commit:
            skip(name, f"ahead commit {upstream_commit[:8]} is contained in upstream")
            continue
        if len(ahead_commits) != ahead_by:
            skip(name, f"could not verify every ahead commit (ahead_by {ahead_by}, verified {len(ahead_commits)})")
            continue
        source_files = scorable_files(cmp["files"])
        if not source_files:
            skip(name, f"no scorable source change (compare files {len(cmp['files'])})")
            continue
        if name in rejected:
            skip(name, "manual rejection: " + rejected[name])
            continue
        row = {
            "name": name, "qnx_repo": f"https://github.com/qnx-ports/{name}",
            "qnx_branch": branch, "qnx_head_sha": head_sha, "upstream": upstream,
            "upstream_base_ref": base_ref, "upstream_base_sha": cmp["merge_base_commit"]["sha"],
            "compare_status": cmp["status"], "ahead_by": ahead_by,
            "behind_by": cmp.get("behind_by", 0), "compare_files": len(cmp["files"]),
            "ahead_commits": ahead_commits, "scorable_source_files": source_files,
        }
        selected.append(row)
    return selected, skipped, 0, names


def yaml_snippet(rows: list[dict]) -> str:
    lines = []
    for p in rows:
        fields = [("name", p["name"]), ("qnx_repo", p["qnx_repo"]), ("qnx_branch", p["qnx_branch"]),
                  ("qnx_head_sha", p["qnx_head_sha"]), ("upstream", p["upstream"]),
                  ("upstream_base_ref", p["upstream_base_ref"]), ("upstream_base_sha", p["upstream_base_sha"]),
                  ("extraction", "git-diff-fork"), ("compare_status", p["compare_status"]),
                  ("ahead_by", p["ahead_by"]), ("behind_by", p["behind_by"]),
                  ("compare_files", p["compare_files"]), ("expected_scope", "source"), ("verified", True)]
        lines.append(f"  - name: {json.dumps(fields[0][1], ensure_ascii=False)}")
        for key, value in fields[1:]:
            val = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else str(value).lower() if isinstance(value, bool) else str(value)
            lines.append(f"    {key}: {val}")
        subjects = " | ".join(c["subject"] for c in p["ahead_commits"])
        note = ("QNX commits: " + subjects)[:300]
        lines.append(f"    note: {json.dumps(note, ensure_ascii=False)}")
        lines.append("    split: fresh")
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=15)
    parser.add_argument("--minimum", type=int, default=10)
    parser.add_argument("--out", default=str(EVAL / "tools/fresh_selection.json"))
    parser.add_argument("--yaml-snippet", metavar="FILE")
    parser.add_argument("--reject", action="append", default=[])
    args = parser.parse_args(argv)
    rejected = reject_map(args.reject)
    selected, skipped, not_examined, names = enumerate_candidates(args.target, rejected)
    decided = {r["name"]: r["reason"] for r in skipped}
    decided.update({r["name"]: "selected" for r in selected})
    for name in names:
        if name in decided:
            print(f"{name}: {decided[name]}", file=sys.stderr)
    for row in selected:
        print(f"{row['name']}: ahead subjects: " + " | ".join(c["subject"] for c in row["ahead_commits"]), file=sys.stderr)
    now = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    payload = {"generated_at": now, "criteria_commit": commit, "repo_list_length": len(names),
               "selected": selected, "skipped": skipped, "not_examined_after_stop": not_examined}
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.yaml_snippet:
        Path(args.yaml_snippet).write_text(yaml_snippet(selected), encoding="utf-8")
    if len(selected) < args.minimum:
        print(f"Only {len(selected)} selected; minimum is {args.minimum}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
