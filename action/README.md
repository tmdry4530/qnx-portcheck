# qnx-portcheck GitHub Action

Use this composite action to scan a checkout and optionally upload its SARIF findings to GitHub code scanning. It runs the host-side `qnx-portcheck` tool; it never runs anything on a QNX target.

```yaml
- uses: actions/checkout@v5
- uses: Heal-chamdom/qnx-portcheck/action@main
  with:
    path: "."
```

Inputs: `path` (default `.`), `sarif-file` (default `qnx-portcheck.sarif`), `python-version` (default `3.12`), `upload` (default `true`), and `category` (default `qnx-portcheck`). Output: `sarif-file`, the generated SARIF path. Uploading requires workflow permission `security-events: write` (and normally `contents: read`). For pull requests from forks, GitHub does not grant write tokens, so upload may be skipped or fail; set `upload: "false"` and use `actions/upload-artifact` if needed. The example workflow is at `../examples/workflows/qnx-portcheck.yml`; pin the action to a commit SHA for production use.
