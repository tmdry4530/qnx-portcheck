"""Evaluate qnx-portcheck against portability patches in the project corpus."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path, PurePosixPath
from statistics import mean
from typing import Any

HARNESS_VERSION = "0.1.0"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SOURCE_EXTS = {
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".cxx",
    ".c++",
    ".hpp",
    ".hh",
    ".hxx",
    ".h++",
    ".ipp",
    ".inl",
    ".tcc",
    ".ixx",
}
BUILD_NAMES = {
    "CMakeLists.txt",
    "Makefile",
    "makefile",
    "GNUmakefile",
    "Makefile.am",
    "Makefile.in",
    "configure",
    "configure.ac",
    "configure.in",
    "meson.build",
    "meson_options.txt",
    "meson.options",
    "wscript",
    "SConstruct",
    "SConscript",
    "BUILD",
    "BUILD.bazel",
    "WORKSPACE",
    "WORKSPACE.bazel",
    "MODULE.bazel",
    "build.ninja",
    "Kconfig",
    ".gitmodules",
    "CMakePresets.json",
}
BUILD_EXTS = {".cmake", ".mk", ".am", ".ac", ".m4", ".bzl", ".gn", ".gni", ".pro", ".pri", ".bazel"}
TEST_COMPONENTS = {
    "test",
    "tests",
    "testing",
    "testcode",
    "testes",
    "unittest",
    "unittests",
    "gtest",
    "testsuite",
}
REQUIRED = ("name", "upstream", "upstream_base_sha", "qnx_repo", "qnx_head_sha", "extraction")
SPLIT_RULE = "Projects sorted by name using Python's case-sensitive string ordering alternate by index: even to tune, odd to holdout."


def assign_splits(projects: list[dict]) -> dict[str, str]:
    """Sort the full project names with plain Python string ordering (case-sensitive, code-point order); assign indexes 0, 2, 4, ... to tune and indexes 1, 3, 5, ... to holdout."""
    names = sorted(p["name"] for p in projects)
    return {name: ("tune" if i % 2 == 0 else "holdout") for i, name in enumerate(names)}


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int


@dataclass
class FilePatch:
    old_path: str | None
    new_path: str | None
    status: str
    hunks: list[Hunk] = field(default_factory=list)
    is_binary: bool = False
    old_mode: str | None = None
    new_mode: str | None = None


@dataclass
class Site:
    file: str
    category: str
    is_test: bool
    kind: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    target_lines: list[int]
    hunks: int = 1


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid quoted scalar {value!r}: {exc}") from exc
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() in {"null", "~"}:
        return None
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return value


def _mini_yaml_load(text: str) -> Any:
    """Load the deliberately small YAML subset used by projects.yaml."""
    projects: list[dict[str, Any]] = []
    in_projects = False
    current: dict[str, Any] | None = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "projects:":
            in_projects = True
            continue
        if not in_projects:
            raise ValueError(f"unsupported YAML at line {number}: expected projects:")
        match = re.fullmatch(r"  - ([A-Za-z_][\w-]*):\s*(.*)", line)
        if match:
            current = {}
            projects.append(current)
            current[match.group(1)] = _scalar(match.group(2))
            continue
        match = re.fullmatch(r"    ([A-Za-z_][\w-]*):\s*(.*)", line)
        if match and current is not None:
            current[match.group(1)] = _scalar(match.group(2))
            continue
        raise ValueError(f"unsupported YAML at line {number}: {raw}")
    return {"projects": projects}


def validate_project(p: dict[str, Any]) -> None:
    for key in REQUIRED:
        if key not in p or p[key] in (None, ""):
            raise ValueError(f"project missing required field: {key}")
    for key in ("upstream_base_sha", "qnx_head_sha"):
        if not isinstance(p[key], str) or not SHA_RE.fullmatch(p[key]):
            raise ValueError(f"{key} must be a 40-character hexadecimal SHA")
    if p["extraction"] != "git-diff-fork":
        raise ValueError(f"unknown extraction method: {p['extraction']}")


def load_projects(path: str | Path, prefer_yaml: bool = True) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    data = None
    if prefer_yaml:
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(text)
        except ImportError:
            pass
    if data is None:
        data = _mini_yaml_load(text)
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError("projects file must contain a projects list")
    projects = data["projects"]
    names: set[str] = set()
    for p in projects:
        if not isinstance(p, dict):
            raise ValueError("each project must be a mapping")
        validate_project(p)
        if p["name"] in names:
            raise ValueError(f"duplicate project name: {p['name']}")
        names.add(p["name"])
    return projects


def classify_path(path: str) -> str:
    p = PurePosixPath(str(path).replace("\\", "/"))
    ext = p.suffix.lower()
    if ext in SOURCE_EXTS or (p.name.endswith(".C")):
        return "source"
    if p.name in BUILD_NAMES or ext in BUILD_EXTS:
        return "build"
    return "other"


def is_test_path(path: str) -> bool:
    p = PurePosixPath(str(path).replace("\\", "/"))
    if any(part.lower() in TEST_COMPONENTS for part in p.parts):
        return True
    name = p.name.lower()
    return bool(re.match(r"^(?:.*_test\..*|.*_unittest\..*|test_.*\..*|.*-test\..*)$", name))


def _strip_prefix(path: str) -> str:
    if path == "/dev/null":
        return path
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def _diff_path(line: str) -> str:
    raw = line[4:]
    if raw == "/dev/null":
        return raw
    # Unified diff paths normally have no timestamp; preserve spaces verbatim.
    return _strip_prefix(raw)


def parse_unified_diff(text: str) -> list[FilePatch]:
    patches: list[FilePatch] = []
    current: FilePatch | None = None
    pending_old: str | None = None
    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line[len("diff --git ") :].split(" ", 1)
            old = _strip_prefix(parts[0]) if parts else None
            new = _strip_prefix(parts[1]) if len(parts) > 1 else None
            current = FilePatch(old, new, "modified")
            patches.append(current)
            pending_old = None
        elif current is None:
            continue
        elif line.startswith("new file mode "):
            current.status = "added"
            current.new_mode = line.split()[-1]
        elif line.startswith("deleted file mode "):
            current.status = "deleted"
            current.old_mode = line.split()[-1]
        elif line.startswith("old mode "):
            current.old_mode = line.split()[-1]
        elif line.startswith("new mode "):
            current.new_mode = line.split()[-1]
        elif line.startswith("index ") and line.rstrip().endswith("160000"):
            current.status = "submodule"
        elif line.startswith("rename from "):
            current.old_path = line[len("rename from ") :]
            current.status = "renamed"
        elif line.startswith("rename to "):
            current.new_path = line[len("rename to ") :]
            current.status = "renamed"
        elif line.startswith("--- "):
            pending_old = _diff_path(line)
            if pending_old == "/dev/null":
                current.status = "added"
            else:
                current.old_path = pending_old
        elif line.startswith("+++ "):
            new = _diff_path(line)
            if new == "/dev/null":
                current.status = "deleted"
            else:
                current.new_path = new
        elif line.startswith("Binary files ") or line.startswith("GIT binary patch"):
            current.is_binary = True
            current.status = "binary"
        elif line.startswith("@@ "):
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if match:
                nums = match.groups()
                current.hunks.append(Hunk(int(nums[0]), int(nums[1] or 1), int(nums[2]), int(nums[3] or 1)))
        elif "Subproject commit " in line:
            current.status = "submodule"
    for p in patches:
        if p.old_mode == "160000" or p.new_mode == "160000":
            p.status = "submodule"
        elif p.is_binary:
            p.status = "binary"
        elif (
            p.status not in {"added", "deleted", "renamed", "submodule", "binary"}
            and p.old_mode
            and p.new_mode
            and p.old_mode != p.new_mode
            and not p.hunks
        ):
            p.status = "modified"
        elif p.status == "modified" and p.old_path != p.new_path:
            p.status = "renamed"
    return patches


def build_out_of_scope(file_patches: list[FilePatch]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {
        "new_files": [],
        "binary": [],
        "submodule": [],
        "mode_only": [],
        "rename_only": [],
        "deleted_empty": [],
    }
    for patch in file_patches:
        path = patch.old_path or patch.new_path or ""
        if patch.status == "added":
            out["new_files"].append(
                {
                    "path": patch.new_path or path,
                    "category": classify_path(patch.new_path or path),
                    "added_lines": sum(h.new_count for h in patch.hunks),
                }
            )
        elif patch.status == "binary":
            out["binary"].append(path)
        elif patch.status == "submodule":
            out["submodule"].append(path)
        elif patch.status == "renamed" and not patch.hunks:
            out["rename_only"].append({"old_path": patch.old_path, "new_path": patch.new_path})
        elif patch.status == "deleted" and not patch.hunks:
            out["deleted_empty"].append(path)
        elif (
            patch.old_mode != patch.new_mode
            and not patch.hunks
            and patch.status not in {"renamed", "added", "deleted"}
        ):
            out["mode_only"].append(path)
    return out


def build_sites(file_patches: list[FilePatch], merge_gap: int = 0) -> list[Site]:
    sites: list[Site] = []
    for patch in file_patches:
        path = patch.old_path or patch.new_path or ""
        cat = classify_path(path)
        if patch.status in {"added", "binary", "submodule"} or not patch.hunks:
            continue
        file_sites = []
        for h in sorted(patch.hunks, key=lambda item: item.old_start):
            if h.old_count:
                targets = list(range(h.old_start, h.old_start + h.old_count))
                kind = "modify" if h.new_count else "delete"
            else:
                targets = [n for n in (h.old_start, h.old_start + 1) if n >= 1]
                kind = "insert"
            file_sites.append(
                Site(
                    path,
                    cat,
                    is_test_path(path),
                    kind,
                    h.old_start,
                    h.old_count,
                    h.new_start,
                    h.new_count,
                    targets,
                )
            )
        for site in file_sites:
            if sites and sites[-1].file == site.file and sites[-1].category == site.category:
                previous = sites[-1]
                gap = min(site.target_lines) - max(previous.target_lines)
                if gap <= merge_gap:
                    previous.target_lines = sorted(set(previous.target_lines + site.target_lines))
                    previous.kind = previous.kind if previous.kind == site.kind else "mixed"
                    previous.old_start = min(previous.old_start, site.old_start)
                    previous.old_count = max(previous.target_lines) - min(previous.target_lines) + 1
                    previous.new_count += site.new_count
                    previous.hunks += site.hunks
                    continue
            sites.append(site)
    return sites


def _norm_file(path: Any) -> str:
    return PurePosixPath(str(path).replace("\\", "/")).as_posix().removeprefix("./")


def match_findings(findings: list[dict], sites: list[Site], window: int) -> dict:
    by_finding: list[list[int]] = []
    by_site: list[list[int]] = [[] for _ in sites]
    for fi, finding in enumerate(findings):
        line = finding.get("line")
        matched = []
        if isinstance(line, int) and not isinstance(line, bool) and line >= 1:
            file = _norm_file(finding.get("file", ""))
            for si, site in enumerate(sites):
                if _norm_file(site.file) == file and any(
                    abs(line - target) <= window for target in site.target_lines
                ):
                    matched.append(si)
                    by_site[si].append(fi)
        by_finding.append(matched)
    return {"finding_sites": by_finding, "site_findings": by_site}


def _ratio(n: int, d: int) -> float | None:
    return round(n / d, 4) if d else None


def compute_metrics(
    sites: list[Site], findings: list[dict], match: dict, patched_files: set[str] | list[str]
) -> dict:
    by_cat = {c: sum(s.category == c for s in sites) for c in ("source", "build", "other")}
    hit_cat = {
        c: sum(bool(match["site_findings"][i]) and s.category == c for i, s in enumerate(sites))
        for c in by_cat
    }
    src_non = sum(s.category == "source" and not s.is_test for s in sites)
    src_test = sum(s.category == "source" and s.is_test for s in sites)
    hit_src_non = sum(
        bool(match["site_findings"][i]) and s.category == "source" and not s.is_test
        for i, s in enumerate(sites)
    )
    tp_indexes = {
        i
        for i, sis in enumerate(match["finding_sites"])
        if any(sites[j].category in {"source", "build"} for j in sis)
    }
    findings_by = {
        c: sum(classify_path(f.get("file", "")) == c for f in findings) for c in ("source", "build", "other")
    }
    patched = {_norm_file(x) for x in patched_files}
    in_patch = [i for i, f in enumerate(findings) if _norm_file(f.get("file", "")) in patched]
    tp_patch = sum(i in tp_indexes for i in in_patch)
    return {
        "sites_total": len(sites),
        "sites_by_category": by_cat,
        "sites_source_nontest": src_non,
        "sites_source_test": src_test,
        "sites_hit_source_nontest": hit_src_non,
        "sites_hit_by_category": hit_cat,
        "recall_source": _ratio(hit_cat["source"], by_cat["source"]),
        "recall_source_nontest": _ratio(hit_src_non, src_non),
        "recall_build": _ratio(hit_cat["build"], by_cat["build"]),
        "recall_in_scope": _ratio(hit_cat["source"] + hit_cat["build"], by_cat["source"] + by_cat["build"]),
        "findings_total": len(findings),
        "findings_tp": len(tp_indexes),
        "findings_by_category": findings_by,
        "findings_in_patched_files": len(in_patch),
        "findings_tp_in_patched_files": tp_patch,
        "precision": _ratio(len(tp_indexes), len(findings)),
        "precision_in_patched_files": _ratio(tp_patch, len(in_patch)),
    }


def aggregate(project_results: list[dict]) -> dict:
    ok = [p for p in project_results if p.get("status") == "ok"]
    ratios = (
        "recall_source",
        "recall_source_nontest",
        "recall_build",
        "recall_in_scope",
        "precision",
        "precision_in_patched_files",
    )
    count_keys = (
        "sites_total",
        "sites_source_nontest",
        "sites_source_test",
        "sites_hit_source_nontest",
        "findings_total",
        "findings_tp",
    )
    sums = {k: sum(p.get("metrics", {}).get(k, 0) for p in ok) for k in count_keys}
    categories = {
        c: sum(p.get("metrics", {}).get("sites_by_category", {}).get(c, 0) for p in ok)
        for c in ("source", "build", "other")
    }
    hits = {
        c: sum(p.get("metrics", {}).get("sites_hit_by_category", {}).get(c, 0) for p in ok)
        for c in categories
    }
    finding_cats = {
        c: sum(p.get("metrics", {}).get("findings_by_category", {}).get(c, 0) for p in ok) for c in categories
    }
    tp_patch = sum(p.get("metrics", {}).get("findings_tp_in_patched_files", 0) for p in ok)
    n_patch = sum(p.get("metrics", {}).get("findings_in_patched_files", 0) for p in ok)
    micro = {
        "sites_total": sums["sites_total"],
        "sites_source_nontest": sums["sites_source_nontest"],
        "sites_hit_source_nontest": sums["sites_hit_source_nontest"],
        "sites_by_category": categories,
        "sites_hit_by_category": hits,
        "findings_total": sums["findings_total"],
        "findings_tp": sums["findings_tp"],
        "findings_in_patched_files": n_patch,
        "findings_tp_in_patched_files": tp_patch,
        "findings_by_category": finding_cats,
    }
    denoms = {
        "recall_source": categories["source"],
        "recall_source_nontest": sums["sites_source_nontest"],
        "recall_build": categories["build"],
        "recall_in_scope": categories["source"] + categories["build"],
        "precision": sums["findings_total"],
        "precision_in_patched_files": n_patch,
    }
    nums = {
        "recall_source": hits["source"],
        "recall_source_nontest": sum(p.get("metrics", {}).get("sites_hit_source_nontest", 0) for p in ok),
        "recall_build": hits["build"],
        "recall_in_scope": hits["source"] + hits["build"],
        "precision": sums["findings_tp"],
        "precision_in_patched_files": tp_patch,
    }
    micro.update({k: _ratio(nums[k], denoms[k]) for k in ratios})
    macro = {}
    for key in ratios:
        vals = [p.get("metrics", {}).get(key) for p in ok if p.get("metrics", {}).get(key) is not None]
        macro[key] = {"mean": round(mean(vals), 4) if vals else None, "n": len(vals)}
    by_rule: dict[str, dict[str, Any]] = {}
    for project in ok:
        project_name = project.get("project", {}).get("name", project.get("name", ""))
        sites = project.get("sites", [])
        for finding in project.get("findings", []):
            rule = finding.get("rule_id", "")
            row = by_rule.setdefault(rule, {"findings": 0, "findings_tp": 0, "_sites": set()})
            row["findings"] += 1
            hit_sites = finding.get("matched_sites", [])
            tp = any(
                0 <= i < len(sites) and sites[i].get("category") in {"source", "build"} for i in hit_sites
            )
            row["findings_tp"] += int(tp)
            for i in hit_sites:
                if 0 <= i < len(sites) and sites[i].get("category") in {"source", "build"}:
                    row["_sites"].add((project_name, i))
    for row in by_rule.values():
        row["sites_hit"] = len(row.pop("_sites"))
    return {
        "counts": {
            "ok_projects": len(ok),
            "error_projects": sum(p.get("status") == "error" for p in project_results),
        },
        "micro": micro,
        "macro": macro,
        "by_rule": by_rule,
    }


def validate_scan_output(obj: Any) -> list[dict]:
    def need(cond: bool, message: str) -> None:
        if not cond:
            raise ValueError(message)

    need(isinstance(obj, dict), "scan output must be an object")
    for key in ("tool", "version", "root"):
        need(isinstance(obj.get(key), str), f"{key} must be a string")
    fs = obj.get("findings")
    need(isinstance(fs, list), "findings must be a list")
    for i, f in enumerate(fs):
        pre = f"findings[{i}]"
        need(isinstance(f, dict), f"{pre} must be an object")
        for key in ("rule_id", "file", "message", "suggestion"):
            need(isinstance(f.get(key), str), f"{pre}.{key} must be a string")
        need(f.get("severity") in {"error", "warning", "note"}, f"{pre}.severity is invalid")
        need(
            isinstance(f.get("line"), int) and not isinstance(f.get("line"), bool) and f["line"] >= 1,
            f"{pre}.line must be an integer >= 1",
        )
        need(
            f.get("col") is None or (isinstance(f.get("col"), int) and not isinstance(f.get("col"), bool)),
            f"{pre}.col must be an integer or null",
        )
        need(
            f.get("doc_url") is None or isinstance(f.get("doc_url"), str),
            f"{pre}.doc_url must be a string or null",
        )
        need(f.get("confidence") in {"high", "medium", "manual-review"}, f"{pre}.confidence is invalid")
    return fs


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", "surrogateescape")


def _json_safe(value: Any) -> Any:
    if isinstance(value, str):
        return value.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {_json_safe(key): _json_safe(item) for key, item in value.items()}
    return value


def _git(repo: Path, *args: str, timeout: int = 600, check: bool = True) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    cp = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if check and cp.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {_decode_output(cp.stderr).strip()}")
    return cp


def _git_url(url: str) -> str:
    return url + ".git" if url.startswith("https://github.com/") and not url.endswith(".git") else url


def fetch_project(p: dict, work_dir: str | Path, timeout: int) -> Path:
    dest = Path(work_dir) / p["name"]
    if dest.exists():
        cp = _git(dest, "rev-parse", "HEAD", timeout=timeout, check=False)
        obj = _git(dest, "cat-file", "-e", p["upstream_base_sha"] + "^{commit}", timeout=timeout, check=False)
        if (
            cp.returncode == 0
            and _decode_output(cp.stdout).strip() == p["upstream_base_sha"]
            and obj.returncode == 0
        ):
            return dest
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir()
    _git(dest, "init", "-q", timeout=timeout)
    _git(
        dest,
        "fetch",
        "-q",
        "--depth=1",
        "--no-tags",
        _git_url(p["upstream"]),
        p["upstream_base_sha"],
        timeout=timeout,
    )
    _git(
        dest,
        "-c",
        "advice.detachedHead=false",
        "checkout",
        "-q",
        "--detach",
        p["upstream_base_sha"],
        timeout=timeout,
    )
    _git(
        dest,
        "fetch",
        "-q",
        "--depth=1",
        "--no-tags",
        _git_url(p["qnx_repo"]),
        p["qnx_head_sha"],
        timeout=timeout,
    )
    head = _decode_output(_git(dest, "rev-parse", "HEAD", timeout=timeout).stdout).strip()
    if head != p["upstream_base_sha"]:
        raise RuntimeError(f"checkout HEAD {head} does not match upstream base SHA")
    return dest


def get_patch_diff(repo_dir: str | Path, base: str, head: str) -> bytes:
    return _git(Path(repo_dir), "diff", "-U0", "--no-color", "--no-ext-diff", "-M", base, head).stdout


def run_scan(scan_cmd_template: str, path: str | Path, timeout: int) -> tuple[dict, float]:
    repo_root = Path(__file__).resolve().parent.parent
    absolute = str(Path(path).resolve())
    cmd = [token.replace("{path}", absolute) for token in shlex.split(scan_cmd_template)]
    start = time.monotonic()
    cp = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    elapsed = time.monotonic() - start
    stderr = _decode_output(cp.stderr).strip()
    if cp.returncode == 2:
        raise RuntimeError(f"scanner usage error (exit 2): {stderr[:500]}")
    if cp.returncode not in (0, 1):
        raise RuntimeError(f"scanner exited with status {cp.returncode}: {stderr}")
    try:
        obj = json.loads(_decode_output(cp.stdout))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"scanner exited {cp.returncode} without valid JSON: {exc}; {_decode_output(cp.stderr).strip()}"
        ) from exc
    validate_scan_output(obj)
    return obj, elapsed


def _kst_now() -> str:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    except Exception:
        return datetime.now(timezone(timedelta(hours=9))).isoformat()


def evaluate_project(p: dict, args: argparse.Namespace) -> dict:
    start = time.monotonic()
    base_meta = {
        k: p.get(k)
        for k in (
            "name",
            "upstream",
            "upstream_base_ref",
            "upstream_base_sha",
            "qnx_repo",
            "qnx_branch",
            "qnx_head_sha",
            "expected_scope",
            "verified",
        )
    }
    result = {
        "label": args.label,
        "harness_version": HARNESS_VERSION,
        "generated_at": _kst_now(),
        "project": base_meta,
        "window": args.window,
        "merge_gap": args.merge_gap,
        "scan_cmd": args.scan_cmd,
        "scanner_source_commit": getattr(args, "scanner_source_commit", None),
        "durations": {"fetch": 0.0, "scan": 0.0},
        "diff_stats": {
            "files_changed": 0,
            "compare_files_expected": p.get("compare_files"),
            "compare_files_match": None,
        },
        "patched_files": [],
        "sites": [],
        "out_of_scope": {
            "new_files": [],
            "binary": [],
            "submodule": [],
            "mode_only": [],
            "build_sites": 0,
            "other_sites": 0,
        },
        "findings": [],
        "metrics": {},
        "status": "error",
    }
    phase = "other"
    try:
        t = time.monotonic()
        phase = "fetch"
        repo = fetch_project(p, args.work_dir, args.timeout)
        result["durations"]["fetch"] = time.monotonic() - t
        phase = "other"
        diff = get_patch_diff(repo, p["upstream_base_sha"], p["qnx_head_sha"])
        Path(args.work_dir).mkdir(parents=True, exist_ok=True)
        Path(args.work_dir, p["name"] + ".qnx.diff").write_bytes(diff)
        patches = parse_unified_diff(_decode_output(diff))
        result["diff_stats"] = {
            "files_changed": len(patches),
            "compare_files_expected": p.get("compare_files"),
            "compare_files_match": (
                len(patches) == p.get("compare_files") if p.get("compare_files") is not None else None
            ),
        }
        sites = build_sites(patches, args.merge_gap)
        out = build_out_of_scope(patches)
        result["out_of_scope"].update(out)
        result["out_of_scope"]["build_sites"] = sum(s.category == "build" for s in sites)
        result["out_of_scope"]["other_sites"] = sum(s.category == "other" for s in sites)
        phase = "scanner"
        finding_obj, scan_duration = run_scan(args.scan_cmd, repo, args.timeout)
        result["durations"]["scan"] = scan_duration
        findings = finding_obj["findings"]
        match = match_findings(findings, sites, args.window)
        patched = sorted({s.file for s in sites})
        result["patched_files"] = patched
        result["sites"] = [
            {**asdict(site), "matched_findings": match["site_findings"][i]} for i, site in enumerate(sites)
        ]
        result["findings"] = [
            {**f, "matched_sites": match["finding_sites"][i]} for i, f in enumerate(findings)
        ]
        metrics = compute_metrics(sites, findings, match, patched)
        result["metrics"] = metrics
        result["scanner"] = {"tool": finding_obj["tool"], "version": finding_obj["version"]}
        result["status"] = "ok"
    except Exception as exc:
        work_prefix = str(Path(args.work_dir).resolve())
        message = f"{type(exc).__name__}: {exc}".replace(work_prefix, "eval/work")
        result["error"] = message[:300]
        if isinstance(exc, subprocess.TimeoutExpired):
            result["error_kind"] = "timeout"
        elif phase == "scanner" and isinstance(exc, RuntimeError) and "usage error (exit 2)" in str(exc):
            result["error_kind"] = "usage"
        elif phase == "scanner":
            result["error_kind"] = "scanner"
        elif phase == "fetch":
            result["error_kind"] = "fetch"
        else:
            result["error_kind"] = "other"
    return result


def _fmt(v: Any) -> str:
    return "—" if v is None else f"{v:.3f}"


def render_summary_md(summary: dict) -> str:
    cfg = summary.get("run_config", {})
    label = str(cfg.get("label", ""))
    out = []
    if "FAKE" in label.upper():
        out += [
            "> **FAKE-SCAN harness smoke results — produced with eval/fake_scan.py, NOT qnx-portcheck. These numbers only show the harness works end-to-end; they are NOT real metrics.**",
            "",
        ]
    out += [
        "# qnx-portcheck evaluation results",
        "",
    ]
    if "FAKE" not in label.upper():
        out += [
            "Numbers below come from an actual run of qnx-portcheck on the upstream base commits listed in eval/projects.yaml, compared with the qnx-ports patches (see METHOD.md). The tool was not run on a QNX target.",
            "",
        ]
    out += [
        f"- Label: {label}",
        f"- Date (KST): {cfg.get('date_kst', '—')}",
        f"- Window: ±{cfg.get('window', '—')} lines",
        f"- Merge gap: {cfg.get('merge_gap', '—')} lines",
        f"- Scan command: `{cfg.get('scan_cmd', '—')}`",
        f"- Scanner: {cfg.get('scanner', '—')}",
        f"- Harness version: {cfg.get('harness_version', HARNESS_VERSION)}",
        f"- Scanner source commit: {cfg.get('scanner_source_commit', '—') or '—'}",
        f"- Harness git SHA: {cfg.get('harness_git_sha', '—') or '—'}",
        f"- Total runtime: {cfg.get('total_runtime_seconds', '—')} s",
        f"- Projects: {cfg.get('projects_count', 0)}",
        f"- Reused projects: {cfg.get('reused_projects', 0)}",
        f"- Scan results generated (KST): {cfg.get('generated_at_range', '— to —')}",
        "",
        "| project | split | upstream base | src sites (all/non-test) | build sites | other sites | new files | findings | TP | recall src | recall src non-test | recall build | precision | precision (patched files) | status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for p in summary.get("projects", []):
        m = p.get("metrics", {})
        o = p.get("out_of_scope", {})
        upstream = p.get("upstream_base_sha", p.get("project", {}).get("upstream_base_sha", "—"))
        name = p.get("name", p.get("project", {}).get("name", "—"))
        out.append(
            f"| {name} | {p.get('split', '—')} | `{str(upstream)[:10]}` | {m.get('sites_by_category', {}).get('source', 0)}/{m.get('sites_source_nontest', 0)} | {m.get('sites_by_category', {}).get('build', 0)} | {m.get('sites_by_category', {}).get('other', 0)} | {len(o.get('new_files', []))} | {m.get('findings_total', 0)} | {m.get('findings_tp', 0)} | {_fmt(m.get('recall_source'))} | {_fmt(m.get('recall_source_nontest'))} | {_fmt(m.get('recall_build'))} | {_fmt(m.get('precision'))} | {_fmt(m.get('precision_in_patched_files'))} | {p.get('status')} |"
        )
    agg = summary.get("aggregate", {})
    micro = agg.get("micro", {})
    macro = agg.get("macro", {})
    out.append(
        f"| **Micro** | — | — | {micro.get('sites_by_category', {}).get('source', 0)}/{micro.get('sites_source_nontest', 0)} | {micro.get('sites_by_category', {}).get('build', 0)} | {micro.get('sites_by_category', {}).get('other', 0)} | — | {micro.get('findings_total', 0)} | {micro.get('findings_tp', 0)} | {_fmt(micro.get('recall_source'))} | {_fmt(micro.get('recall_source_nontest'))} | {_fmt(micro.get('recall_build'))} | {_fmt(micro.get('precision'))} | {_fmt(micro.get('precision_in_patched_files'))} | — |"
    )
    macro_ratios = (
        "recall_source",
        "recall_source_nontest",
        "recall_build",
        "precision",
        "precision_in_patched_files",
    )
    out.append(
        "| **Macro** | — | — | — | — | — | — | — | — | "
        + " | ".join(_fmt(macro.get(k, {}).get("mean")) for k in macro_ratios)
        + " | — |"
    )
    out.append(
        "The term “src sites” means source-file change sites in upstream base coordinates; “(non-test)” excludes test paths."
    )
    out += ["", "## Overall (micro)", ""]
    out.append(
        f"Overall (micro): source-site recall {_fmt(micro.get('recall_source'))} ({micro.get('sites_hit_by_category', {}).get('source', 0)}/{micro.get('sites_by_category', {}).get('source', 0)}), non-test source-site recall {_fmt(micro.get('recall_source_nontest'))} ({micro.get('sites_hit_source_nontest', 0)}/{micro.get('sites_source_nontest', 0)}), build-site recall {_fmt(micro.get('recall_build'))} ({micro.get('sites_hit_by_category', {}).get('build', 0)}/{micro.get('sites_by_category', {}).get('build', 0)}), precision {_fmt(micro.get('precision'))} ({micro.get('findings_tp', 0)}/{micro.get('findings_total', 0)}), precision in patched files {_fmt(micro.get('precision_in_patched_files'))} ({micro.get('findings_tp_in_patched_files', 0)}/{micro.get('findings_in_patched_files', 0)})."
    )
    out.append("")
    for split_name in ("tune", "holdout"):
        split_agg = agg.get("by_split", {}).get(split_name)
        count = sum(p.get("split") == split_name for p in summary.get("projects", []))
        if split_agg is None:
            out.append(f"Split {split_name} (micro, 0 projects): — (not run)")
        else:
            sm = split_agg["micro"]
            out.append(
                f"Split {split_name} (micro, {count} projects): source-site recall {_fmt(sm.get('recall_source'))} ({sm.get('sites_hit_by_category', {}).get('source', 0)}/{sm.get('sites_by_category', {}).get('source', 0)}), non-test source-site recall {_fmt(sm.get('recall_source_nontest'))} ({sm.get('sites_hit_source_nontest', 0)}/{sm.get('sites_source_nontest', 0)}), build-site recall {_fmt(sm.get('recall_build'))} ({sm.get('sites_hit_by_category', {}).get('build', 0)}/{sm.get('sites_by_category', {}).get('build', 0)}), precision {_fmt(sm.get('precision'))} ({sm.get('findings_tp', 0)}/{sm.get('findings_total', 0)}), precision in patched files {_fmt(sm.get('precision_in_patched_files'))} ({sm.get('findings_tp_in_patched_files', 0)}/{sm.get('findings_in_patched_files', 0)})."
            )
    splits = summary.get("splits", {})
    out += [
        "",
        "## Splits",
        "",
        splits.get("rule", SPLIT_RULE),
        "",
        f"- Tune: {', '.join(splits.get('tune', [])) or '—'}",
        f"- Holdout: {', '.join(splits.get('holdout', [])) or '—'}",
    ]
    out += [
        "",
        "## Hits by rule",
        "",
        "| rule_id | findings | TP findings | sites hit |",
        "|---|---:|---:|---:|",
    ]
    for rule, counts in sorted(agg.get("by_rule", {}).items()):
        out.append(
            f"| {rule} | {counts.get('findings', 0)} | {counts.get('findings_tp', 0)} | {counts.get('sites_hit', 0)} |"
        )
    out += ["", "## Runtime", "", "| project | fetch seconds | scan seconds |", "|---|---:|---:|"]
    for p in summary.get("projects", []):
        d = p.get("durations", {})
        out.append(f"| {p.get('name', '—')} | {d.get('fetch', 0):.3f} | {d.get('scan', 0):.3f} |")
    out.append(f"Total runtime: {cfg.get('total_runtime_seconds', 0):.1f} seconds.")
    out += ["", "## Out of scope", ""]
    for p in summary.get("projects", []):
        o = p.get("out_of_scope", {})
        name = p.get("name", p.get("project", {}).get("name", "—"))
        paths = [item.get("path", "") for item in o.get("new_files", [])]
        out.append(
            f"- **{name}**: new files {len(paths)} ({', '.join(paths[:5])}); rename-only {len(o.get('rename_only', []))}; deleted-empty {len(o.get('deleted_empty', []))}; binary {len(o.get('binary', []))}; submodule {len(o.get('submodule', []))}; mode-only {len(o.get('mode_only', []))}; build-file change sites {o.get('build_sites', 0)}; other-file change sites {o.get('other_sites', 0)}."
        )
    errors = [p for p in summary.get("projects", []) if p.get("status") == "error"]
    if errors:
        out += ["", "## Errors", ""]
        for p in errors:
            name = p.get("name", p.get("project", {}).get("name", "—"))
            out.append(
                f"- **{name}** [{p.get('error_kind', 'other')}]: {str(p.get('error', 'Unknown error'))[:300]}"
            )
    out += ["", "See [METHOD.md](METHOD.md) for methodology.", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects", default=str(here / "projects.yaml"))
    ap.add_argument("--only")
    ap.add_argument("--scan-cmd", default="qnx-portcheck scan {path} --format json --fail-on never")
    ap.add_argument("--window", type=int, default=3)
    ap.add_argument("--merge-gap", type=int, default=3)
    ap.add_argument("--work-dir", default=str(here / "work"))
    ap.add_argument("--results-dir", default=str(here / "results"))
    ap.add_argument("--label", default="REAL")
    ap.add_argument("--summary", default=str(here / "RESULTS.md"))
    ap.add_argument("--no-summary", action="store_true")
    ap.add_argument("--include-unverified", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--reuse-results", action="store_true")
    ap.add_argument(
        "--require-reuse", action="store_true", help="reuse matching results only; never fetch or scan"
    )
    ap.add_argument("--split", choices=("tune", "holdout", "all"), default="all")
    args = ap.parse_args(argv)
    all_projects = load_projects(args.projects)
    split_by_name = assign_splits(all_projects)
    split_members = {
        "tune": sorted(name for name, split in split_by_name.items() if split == "tune"),
        "holdout": sorted(name for name, split in split_by_name.items() if split == "holdout"),
    }
    projects = list(all_projects)
    if args.split != "all":
        projects = [p for p in projects if split_by_name[p["name"]] == args.split]
    if args.only:
        wanted = {n.strip() for n in args.only.split(",") if n.strip()}
        projects = [p for p in projects if p["name"] in wanted]
    skipped = [p for p in projects if not p.get("verified", False) and not args.include_unverified]
    projects = [p for p in projects if p not in skipped]
    if args.require_reuse:
        args.reuse_results = True
    started_at = _kst_now()
    run_start = time.monotonic()
    source_cp = subprocess.run(
        ["git", "log", "-1", "--format=%h", "--", "src/"],
        cwd=here.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    scanner_source_commit = _decode_output(source_cp.stdout).strip() if source_cp.returncode == 0 else None
    args.scanner_source_commit = scanner_source_commit or None
    results = []
    reused_projects = 0
    outdir = Path(args.results_dir) / args.label.lower()
    for p in projects:
        prior_path = outdir / (p["name"] + ".json")
        if args.reuse_results and prior_path.exists():
            try:
                prior = json.loads(prior_path.read_text(encoding="utf-8"))
                if (
                    prior.get("status") == "ok"
                    and prior.get("project", {}).get("upstream_base_sha") == p["upstream_base_sha"]
                    and prior.get("project", {}).get("qnx_head_sha") == p["qnx_head_sha"]
                    and prior.get("window") == args.window
                    and prior.get("merge_gap") == args.merge_gap
                    and prior.get("scan_cmd") == args.scan_cmd
                    and prior.get("scanner_source_commit") == args.scanner_source_commit
                ):
                    prior["split"] = split_by_name[p["name"]]
                    results.append(prior)
                    reused_projects += 1
                    print(f"[{args.label}] {p['name']}: reused", file=sys.stderr, flush=True)
                    continue
            except (OSError, json.JSONDecodeError):
                pass
        if args.require_reuse:
            meta = {
                k: p.get(k)
                for k in (
                    "name",
                    "upstream",
                    "upstream_base_ref",
                    "upstream_base_sha",
                    "qnx_repo",
                    "qnx_branch",
                    "qnx_head_sha",
                    "expected_scope",
                    "verified",
                )
            }
            results.append(
                {
                    "label": args.label,
                    "generated_at": _kst_now(),
                    "project": meta,
                    "split": split_by_name[p["name"]],
                    "status": "error",
                    "error_kind": "not-reused",
                    "error": "No matching prior result was available; project was not fetched or scanned.",
                    "metrics": {},
                    "out_of_scope": {},
                    "durations": {"fetch": 0.0, "scan": 0.0},
                }
            )
            print(f"[{args.label}] {p['name']}: ERROR no reusable result", file=sys.stderr, flush=True)
            continue
        print(f"[{args.label}] {p['name']} ...", file=sys.stderr, flush=True)
        r = evaluate_project(p, args)
        r["split"] = split_by_name[p["name"]]
        results.append(r)
        if r["status"] == "ok":
            print(f"[{args.label}] {p['name']}: ok", file=sys.stderr, flush=True)
        else:
            print(f"[{args.label}] {p['name']}: ERROR {r.get('error')}", file=sys.stderr, flush=True)
    scanner = next(
        (
            f"{p.get('scanner', {}).get('tool')}/{p.get('scanner', {}).get('version')}"
            for p in results
            if p.get("scanner")
        ),
        "—",
    )
    total_runtime = round(time.monotonic() - run_start, 1)
    finished_at = _kst_now()
    harness_sha = (
        subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=here.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
        or None
    )
    if harness_sha is not None:
        harness_sha = _decode_output(harness_sha).strip()
    compact = [
        {
            "name": r["project"]["name"],
            "upstream": r["project"].get("upstream"),
            "upstream_base_sha": r["project"].get("upstream_base_sha"),
            "qnx_head_sha": r["project"].get("qnx_head_sha"),
            "status": r["status"],
            "split": r.get("split", split_by_name[r["project"]["name"]]),
            "error": r.get("error"),
            "error_kind": r.get("error_kind"),
            "metrics": r.get("metrics", {}),
            "out_of_scope": r.get("out_of_scope", {}),
            "diff_stats": r.get("diff_stats", {}),
            "scanner": r.get("scanner", {}),
            "durations": {k: round(v, 3) for k, v in r.get("durations", {}).items()},
        }
        for r in results
    ]
    summary = {
        "run_config": {
            "label": args.label,
            "date_kst": _kst_now(),
            "window": args.window,
            "merge_gap": args.merge_gap,
            "scan_cmd": args.scan_cmd,
            "scanner": scanner,
            "harness_version": HARNESS_VERSION,
            "harness_git_sha": harness_sha,
            "scanner_source_commit": scanner_source_commit or None,
            "total_runtime_seconds": total_runtime,
            "started_at": started_at,
            "finished_at": finished_at,
            "projects_count": len(projects),
            "reused_projects": reused_projects,
            "skipped_unverified": len(skipped),
            "split": args.split,
            "generated_at_range": (
                f"{min(r['generated_at'] for r in results if r.get('generated_at'))} to {max(r['generated_at'] for r in results if r.get('generated_at'))}"
                if any(r.get("generated_at") for r in results)
                else "— to —"
            ),
        },
        "splits": {"rule": SPLIT_RULE, **split_members},
        "aggregate": {
            **aggregate(results),
            "by_split": {
                split: aggregate([r for r in results if r.get("split") == split])
                for split in ("tune", "holdout")
                if any(r.get("split") == split for r in results)
            },
        },
        "projects": compact,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    for r in results:
        (outdir / (r["project"]["name"] + ".json")).write_text(
            json.dumps(_json_safe(r), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    (outdir / "summary.json").write_text(
        json.dumps(_json_safe(summary), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if not args.no_summary:
        Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary).write_text(render_summary_md(summary), encoding="utf-8")
    return 2 if results and all(r["status"] == "error" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
