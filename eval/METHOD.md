# Evaluation method

This directory measures how well `qnx-portcheck scan` points at the code that real QNX ports had to change.
The ground truth is the set of patches that the public [qnx-ports](https://github.com/qnx-ports) organization
applied to upstream open-source projects. The tool was **not** run on a QNX target; it is a host tool, and the
evaluation compares its static findings with those existing patches.

## Corpus (`projects.yaml`)

Each entry pins two commits:

- `upstream_base_sha`: the upstream commit the port starts from. It is the `merge_base_commit` returned by the
  GitHub compare API for `<upstream>:<upstream_base_ref>...qnx-ports:<qnx_branch>`.
- `qnx_head_sha`: the head of the qnx-ports branch (`gh api repos/qnx-ports/<repo>/branches/<branch>`).

Both were read with `gh api` (read-only) on 2026-11-15 KST. A project was kept only when the commits between
base and head are QNX port commits (checked by hand from the compare commit list). Candidates whose branches mix
in upstream release commits, or that have no QNX commits, were excluded; the list and reasons are at the end of
`projects.yaml`. `compare_files` is the changed-file count from the compare API; every run checks that
`git diff` reproduces the same count (`diff_stats.compare_files_match` in each result file).

`expected_scope: build-only` marks the six projects whose QNX patch touches only build files.

## Patch extraction

For each project `run_eval.py`:

1. creates `eval/work/<name>/` (git-ignored), fetches `upstream_base_sha` from the upstream repository with
   `git fetch --depth=1`, and checks it out detached (no submodules);
2. fetches `qnx_head_sha` from the qnx-ports fork with `git fetch --depth=1`;
3. runs `git diff -U0 --no-color --no-ext-diff -M <base> <head>` and saves it as `eval/work/<name>.qnx.diff`;
4. parses the diff into files and hunks (`@@ -a,b +c,d @@`, missing count = 1).

No GitHub API call or token is needed at evaluation time; only public git fetches.

## Change sites (ground truth, in upstream base coordinates)

The scanner runs on the **upstream base**, so every change is mapped to base (old-side) line numbers:

- a hunk that deletes or replaces old lines `a..a+b-1` targets exactly those lines;
- a pure insertion after old line `a` (`b = 0`) targets lines `a` and `a+1` (only `1` when `a = 0`).

Hunks in the same file whose target lines are at most `--merge-gap` lines apart (default 3) are merged into one
**site**. This makes an `#ifndef __QNX__` / `#endif` pair around one statement a single site, not two.

Each site gets a category from its file path:

| category | files |
|---|---|
| `source` | C/C++: `.c .h .cc .cpp .cxx .c++ .hpp .hh .hxx .h++ .ipp .inl .tcc .ixx .C` |
| `build` | `CMakeLists.txt`, `Makefile*`, `configure*`, `meson.build`, `wscript`, SCons, Bazel, `.gitmodules`, and `.cmake .mk .am .ac .m4 .bzl .gn .gni .pro .pri .bazel` |
| `other` | everything else (docs, Python/Lua tests, scripts, init files) |

Source sites in test paths (`test/`, `tests/`, `testcode/`, `testes/`, `*_test.*`, `*_unittest.*`, ...) are
also counted separately as "test" so recall can be reported with and without them.

### Out of scope (reported, not scored)

- **new files** added by the patch (e.g. `sys_qnx.c`, `lib/system/qnx/*`): they do not exist in the base, so no
  scanner finding can point at them. They are listed per project.
- binary files, submodule pointer changes, rename-only and mode-only changes, deleted empty files.
- `other` sites are listed but excluded from recall and from true positives.

## Matching rule

A finding `(file, line)` matches a site when the file path is identical (POSIX, relative to the repository root,
leading `./` removed) and `|line - t| <= window` for some target line `t` of the site. The default window is
**±3 lines**. One finding may match several sites and one site may be hit by several findings.

## Metrics

Per project, and overall:

- **recall (source)** = source sites hit by at least one finding / source sites. Also reported for non-test
  source sites and for build sites.
- **precision** = findings that match a source or build site / all findings. This is strict: a finding on code the
  port did not need to change counts as a false positive, even if the construct is genuinely Linux-specific
  (ports often avoid code paths by build configuration instead of editing them).
- **precision (patched files)** = the same ratio over findings in files the patch touched.
- **micro** = sums of counts over all projects, then divided. **macro** = mean of per-project ratios over projects
  where the ratio is defined (`n` is stored in `summary.json`).

Ratios with an empty denominator are shown as `—` (null in JSON).

## Tune / holdout split

To keep rule tuning honest, the corpus is split deterministically into two halves:

- take the **full** project list from `projects.yaml` (before `--only` and before unverified filtering);
- sort it by the `name` field with plain Python string ordering (`sorted(names)`: case-sensitive, Unicode
  code-point order, so `"Zeta"` sorts before `"alpha"`);
- index 0, 2, 4, ... goes to **tune**, index 1, 3, 5, ... goes to **holdout**.

Because membership is computed from the full list, `--only` never moves a project between splits. With the current
33 projects this gives 17 tune and 16 holdout projects; both lists are written to `summary.json` (`splits`) and to
`RESULTS.md` (`## Splits`). Rules should be tuned by looking at tune projects only; holdout numbers are the check.

> **Status (2026-11-15):** the 16 projects in this split's `holdout` half were read during rule tuning on
> dev1/tune (see [TUNING.md](TUNING.md)), so they are now treated as **seen during tuning**, not as a holdout.
> The split name `holdout` is kept in the harness output (`--split holdout`, `Split holdout (micro, ...)`) for
> compatibility only. A fresh holdout set of projects not seen during tuning is being measured separately; its
> numbers are not in this directory yet.

`--split tune|holdout|all` (default `all`) evaluates only that split. Each result records its `split`, and
`summary.json` has `aggregate.by_split`. `RESULTS.md` prints `Split tune (micro, N projects): ...` and
`Split holdout (micro, N projects): ...` right after the `Overall (micro): ...` line, in the same wording.

`--reuse-results` reuses a stored per-project result when the base/head SHAs, window, merge gap, scan command and
scanner source commit all match. `--require-reuse` goes further: a project that cannot be reused is marked
`error` (`error_kind: not-reused`) without fetching or scanning, so results can be re-scored without re-scanning.

## Fresh split (written and committed before any fresh project was selected)

The 16 holdout projects were seen while the rules were tuned (see TUNING.md), so they no longer measure
generalization. The **fresh** split is a new set of projects, chosen by the rules below **before** any scan of them.
Nobody who tunes rules looks at these patches before the measurement is committed.

### Criteria (the same criteria used for the original 33)

A candidate qualifies only if all of these hold:

1. **Upstream port**: a public repository in github.com/qnx-ports that is a GitHub fork of an upstream project
   (`gh api repos/qnx-ports/<repo>` returns a `parent`).
2. **Verifiable merge-base**: the GitHub compare API returns a `merge_base_commit` for
   `<parent>:<base_ref>...qnx-ports:<qnx_branch>` (`qnx_branch` = the fork's default branch), with at least one
   ahead commit and at least one changed file.
3. **QNX-only commits**: none of the ahead commits is an upstream commit. A commit counts as upstream if the
   compare API reports it as contained in the upstream default branch (`<parent>:<default>...<sha>` has status
   `behind` or `identical`), or if its subject is an upstream release/merge of upstream history (e.g. "Bash-4.4
   patch 1", "merge tag 'x' into ..."). Subjects are read by hand and quoted in the `note` field.
4. **Scorable source change**: at least one C/C++ file (extensions as in "Change sites") that exists in the base
   is modified, renamed with changes, or removed. Files only added by the patch do not count.

### Base ref rule (same as for the 33)

From the fork's default branch name, strip a leading `qnx-` or `qnx_`; if something was stripped, try these base
refs in order: `<rest>`, `v<rest>`, `<rest without leading v>`, `release-<rest>`, `<repo>-<rest>`; finally try the
upstream default branch. The first ref whose compare status is `ahead` (behind 0) is used; if none is `ahead`,
the compare against the upstream default branch is used if its status is `diverged`. `upstream_base_sha` is
always the `merge_base_commit` of the chosen compare; `qnx_head_sha` is the head of the fork branch from
`gh api repos/qnx-ports/<repo>/branches/<branch>`.

### Deterministic enumeration and selection

1. List all repositories with `gh api --paginate orgs/qnx-ports/repos` and sort the names with Python `sorted()`
   (case-sensitive, code-point order).
2. Walk the sorted list from the start. Skip a repository, recording the reason, if it is one of the original 33,
   is not a fork, has an upstream (`parent`) repository larger than 500,000 KB by the GitHub `size` field
   (too large to fetch and scan reliably in this harness; decided before selection), has more than 50 ahead
   commits (not reviewable by hand), or fails any criterion above.
3. Take every repository that qualifies, in that order, until 15 are selected (target 12–15, minimum 10).
   Repositories after the 15th are not examined. If fewer than 10 qualify, all qualifying ones are taken and
   the shortfall is reported.
4. Selected projects are added to `projects.yaml` with `split: fresh` and committed before any scan of them.
   After that commit no fresh project is removed or replaced, whatever its results; a project that fails
   technically (fetch, scan, timeout) stays in the list and is reported as failed.

### Split assignment with fresh projects

The tune/holdout even/odd rule is computed over the original 33 projects only (entries without a `split`
field). Projects with `split: fresh` are assigned only by that field and never shift tune/holdout membership.
`Overall (micro)` in RESULTS.md stays computed over the original 33; fresh has its own line.

## Running

```bash
python3 -m venv .venv && .venv/bin/pip install -e . pytest pyyaml
PATH=$PWD/.venv/bin:$PATH .venv/bin/python eval/run_eval.py --label REAL          # real scanner
.venv/bin/python eval/run_eval.py --label FAKE-SCAN --summary eval/RESULTS-FAKE-SCAN.md \
    --scan-cmd "python3 eval/fake_scan.py scan {path} --format json"              # harness smoke test only
.venv/bin/python -m pytest eval/tests -q
```

Options: `--only a,b`, `--window N`, `--merge-gap N`, `--scan-cmd "<cmd with {path}>"`, `--work-dir`,
`--results-dir`, `--timeout`, `--split`, `--reuse-results`, `--require-reuse`. The default scan command is
`qnx-portcheck scan {path} --format json --fail-on never`; exit codes 0 and 1 are accepted with valid JSON,
exit code 2 (usage error) marks the project as failed.

Outputs: `eval/results/<label>/<project>.json` (sites, findings, matches, metrics), `eval/results/<label>/summary.json`,
and `eval/RESULTS.md` (or the `--summary` path). `eval/fake_scan.py` is a token-grep stand-in used only by the
harness tests and the FAKE-SCAN smoke run; its numbers are not tool metrics.
