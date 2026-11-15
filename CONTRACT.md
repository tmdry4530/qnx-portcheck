# qnx-portcheck internal contract (Engineering Lead, 2026-11-15)

Python >=3.10, stdlib-first, package `qnx_portcheck` under src/, CLI entry `qnx-portcheck`, tests with pytest in tests/.
License Apache-2.0. Host tool only; never claims to run on a QNX target.

## CLI
- `qnx-portcheck scan <path> [--format text|json|sarif] [--out FILE]`  (owner: 개발팀1)
- `qnx-portcheck scaffold <path> [--name N] [--out DIR]`             (owner: 개발팀3)
- `qnx-portcheck lint-buildfile <file>` (optional)                     (owner: 개발팀3)

## scan JSON schema (eval depends on this; do not change without telling Engineering Lead)
{"tool":"qnx-portcheck","version":"x.y.z","root":"<abs path>",
 "findings":[{"rule_id":"LNX-EPOLL","severity":"error|warning|note",
   "file":"<path relative to root, posix>","line":123,"col":5,
   "message":"...","suggestion":"...","doc_url":"https://www.qnx.com/developers/docs/8.0/..." or null,
   "confidence":"high|medium|manual-review"}]}

## Rules
- Each rule lives in src/qnx_portcheck/rules/ with id, patterns, suggestion, doc_url.
- doc_url must be a public QNX 8.0 doc page that was actually fetched; record fetch evidence in docs/rule-sources.md.
  If no QNX doc confirms an alternative, suggestion = "manual review" and doc_url = null. Never invent APIs.

## Eval (owner: 개발팀2)
- eval/projects.yaml: >=15 upstream projects ported in github.com/qnx-ports, with upstream base commit SHA and the qnx-ports patch/commit SHA.
- eval/run_eval.py: runs scan on upstream base, compares findings (file,line±window) against lines changed by the qnx-ports patch; outputs eval/results/*.json and eval/RESULTS.md with recall/precision. Numbers only from actual runs; commit raw outputs.

## Rules for everyone
Codex CLI only (`codex exec`), no API keys, no paid services, no myQNX sign-up or SDP download, no force-push, no X posts.
Work on a branch named devN/<topic>; Engineering Lead merges. Do not push to GitHub unless Engineering Lead says so.
