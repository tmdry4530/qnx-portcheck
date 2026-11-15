# Scanner performance fix: evidence

Commit `85a5ca9` (perf(scan)) on branch dev1/tune, parent `7bbc52a`. Measured on the box on 2026-11-15 KST,
8 CPUs, Python from a local venv (`<venv>`), one scan at a time per measurement.

## libwebsockets single scan (byte-for-byte JSON comparison)

Target: upstream base `fbb0baf6af` of libwebsockets (eval/work checkout, 890 C/C++ files + 243 build files).
Command: `qnx-portcheck scan <libwebsockets> --format json --fail-on never`, timed by `timed.py` (wall clock).

| scanner | source | wall time |
|---|---|---:|
| before | `7bbc52a` (`git archive` to /tmp, `PYTHONPATH`) | 724.17 s |
| after | `85a5ca9` | 4.19 s |

(The eval run in RESULTS.md recorded 788.2 s for the same scan with 511aa2e on the same box.)

- `libwebsockets.before.json` and `libwebsockets.after.json` are the two raw outputs.
- `cmp` reports no difference; both files have SHA-256
  `600ca1a26f95c0ae56c0973b609cb883b2d38647c1be6197c05b2f94b18db533` (89 findings). `diff` output is empty.

## Whole corpus (33 projects)

`corpus_cmp.py` re-scanned every eval project with `85a5ca9` and compared all finding fields
(rule_id, severity, file, line, col, message, suggestion, doc_url, confidence) with the findings stored in
`eval/results/real/*.json` (scanner 511aa2e, which has the same rules as 7bbc52a). The old times are the
`durations.scan` values from that eval run.

| project | scan s (511aa2e, eval run) | scan s (perf) | findings old | findings new | identical |
|---|---:|---:|---:|---:|---|
| asio | 14.83 | 1.75 | 16 | 16 | yes |
| avahi | 3.20 | 0.47 | 31 | 31 | yes |
| aws-c-common | 5.32 | 0.63 | 10 | 10 | yes |
| aws-c-io | 6.89 | 0.53 | 20 | 20 | yes |
| c-ares | 3.91 | 0.50 | 17 | 17 | yes |
| check | 1.01 | 0.16 | 4 | 4 | yes |
| chrony | 3.14 | 0.41 | 28 | 28 | yes |
| dlt-daemon | 23.96 | 0.78 | 77 | 77 | yes |
| fribidi | 0.68 | 0.14 | 0 | 0 | yes |
| glog | 0.94 | 0.17 | 21 | 21 | yes |
| gnutls | 19.63 | 2.42 | 15 | 15 | yes |
| googletest | 8.60 | 0.75 | 3 | 3 | yes |
| iperf3 | 1.20 | 0.17 | 20 | 20 | yes |
| jansson | 0.59 | 0.13 | 0 | 0 | yes |
| libevent | 5.04 | 0.61 | 44 | 44 | yes |
| libmetal | 0.71 | 0.18 | 21 | 21 | yes |
| libusb | 6.09 | 0.49 | 20 | 20 | yes |
| libuv | 6.17 | 0.76 | 216 | 216 | yes |
| libwebsockets | 788.22 | 4.15 | 89 | 89 | yes |
| libxml2 | 94.05 | 1.78 | 5 | 5 | yes |
| libyaml | 1.20 | 0.16 | 0 | 0 | yes |
| lldpd | 2.53 | 0.37 | 58 | 58 | yes |
| lua | 1.75 | 0.27 | 1 | 1 | yes |
| mosquitto | 4.24 | 0.52 | 25 | 25 | yes |
| nghttp2 | 15.64 | 1.00 | 8 | 8 | yes |
| ntpsec | 9.29 | 0.68 | 40 | 40 | yes |
| open-amp | 0.47 | 0.11 | 0 | 0 | yes |
| pistache | 14.49 | 0.44 | 54 | 54 | yes |
| re2 | 2.69 | 0.29 | 0 | 0 | yes |
| s2n-tls | 15.14 | 1.83 | 16 | 16 | yes |
| strongswan | 44.28 | 3.87 | 92 | 92 | yes |
| tinyxml2 | 0.71 | 0.11 | 0 | 0 | yes |
| unbound | 17.06 | 1.42 | 24 | 24 | yes |
| **total** | 1123.7 | 28.0 | 975 | 975 | all |

## What changed

- `lexer.lex()`: string-literal prefix regexes were run as `re.match(..., text[index:])` at every code character,
  copying the rest of the file each time (O(n^2)). They are now compiled once and run as
  `pattern.match(text, index)`, only at characters that can start a literal.
- `lexer.position()`: counted newlines from offset 0 for every call (O(n) per finding/literal). It now bisects a
  line-start table cached for the last text.
- `rules.base.include_and_calls()`: compiles its header/call regexes once per rule instead of per file, and skips
  the regex scan when the name does not occur in the file at all.
