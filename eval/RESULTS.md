# qnx-portcheck evaluation results

Numbers below come from an actual run of qnx-portcheck on the upstream base commits listed in eval/projects.yaml, compared with the qnx-ports patches (see METHOD.md). The tool was not run on a QNX target.

- Label: REAL
- Date (KST): 2026-11-15T13:59:56.880379+09:00
- Window: ±3 lines
- Merge gap: 3 lines
- Scan command: `qnx-portcheck scan {path} --format json --fail-on never`
- Scanner: qnx-portcheck/0.1.0
- Harness version: 0.1.0
- Scanner source commit: 511aa2e
- Harness git SHA: 7bbc52a
- Total runtime: 0.0 s
- Projects: 33
- Reused projects: 33
- Scan results generated (KST): 2026-11-15T13:20:09.919449+09:00 to 2026-11-15T13:47:31.477107+09:00

| project | split | upstream base | src sites (all/non-test) | build sites | other sites | new files | findings | TP | recall src | recall src non-test | recall build | precision | precision (patched files) | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| asio | tune | `814f67e730` | 14/8 | 0 | 0 | 0 | 16 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| avahi | holdout | `4294bbff57` | 3/3 | 1 | 1 | 0 | 31 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| aws-c-io | holdout | `bfb0819d39` | 11/11 | 2 | 0 | 0 | 20 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| c-ares | tune | `6508d6ad27` | 16/16 | 17 | 0 | 0 | 17 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| chrony | tune | `d622b222a9` | 11/8 | 3 | 0 | 3 | 28 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| dlt-daemon | holdout | `0f2d4cfffa` | 2/2 | 14 | 0 | 0 | 77 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| glog | holdout | `b33e3bad4c` | 27/14 | 10 | 0 | 0 | 21 | 1 | 0.037 | 0.071 | 0.000 | 0.048 | 0.125 | ok |
| gnutls | tune | `5dd9a55040` | 6/6 | 0 | 0 | 0 | 15 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| googletest | holdout | `b796f7d446` | 3/2 | 9 | 0 | 0 | 3 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| iperf3 | tune | `dfcea9f6a0` | 4/4 | 0 | 0 | 0 | 20 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| libevent | tune | `5df3037d10` | 1/1 | 1 | 0 | 0 | 44 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| libmetal | holdout | `f8a0e51aee` | 0/0 | 2 | 0 | 31 | 21 | 0 | — | — | 0.000 | 0.000 | — | ok |
| libusb | tune | `e782eeb251` | 4/4 | 7 | 0 | 2 | 20 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| libuv | holdout | `5152db2cbf` | 40/19 | 1 | 0 | 0 | 216 | 1 | 0.025 | 0.053 | 0.000 | 0.005 | 0.019 | ok |
| libwebsockets | tune | `fbb0baf6af` | 5/5 | 1 | 0 | 0 | 89 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| libxml2 | holdout | `de918d45e1` | 1/1 | 0 | 0 | 0 | 5 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| lldpd | holdout | `df8d729859` | 22/22 | 3 | 0 | 0 | 58 | 1 | 0.091 | 0.091 | 0.000 | 0.017 | 0.333 | ok |
| lua | tune | `cb88c1cd5d` | 5/5 | 0 | 10 | 1 | 1 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| mosquitto | holdout | `b0277869d9` | 0/0 | 2 | 20 | 7 | 25 | 0 | — | — | 0.000 | 0.000 | — | ok |
| nghttp2 | tune | `526ff38e02` | 1/1 | 3 | 0 | 0 | 8 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| ntpsec | holdout | `39b19ff71b` | 35/32 | 4 | 0 | 0 | 40 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| open-amp | tune | `604cdf9a45` | 4/4 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | — | — | — | ok |
| pistache | holdout | `ddffda861a` | 19/18 | 3 | 1 | 0 | 54 | 7 | 0.316 | 0.278 | 0.000 | 0.130 | 0.438 | ok |
| s2n-tls | holdout | `a7862238a9` | 32/32 | 1 | 0 | 0 | 16 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| strongswan | tune | `4d709df8b2` | 23/22 | 7 | 0 | 0 | 92 | 3 | 0.087 | 0.091 | 0.000 | 0.033 | 0.231 | ok |
| tinyxml2 | holdout | `321ea883b7` | 2/2 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | — | — | — | ok |
| unbound | tune | `a33f0638e1` | 21/16 | 0 | 0 | 0 | 24 | 7 | 0.191 | 0.250 | — | 0.292 | 0.467 | ok |
| aws-c-common | tune | `2b67a658e4` | 0/0 | 3 | 0 | 0 | 10 | 0 | — | — | 0.000 | 0.000 | — | ok |
| check | holdout | `11970a7e11` | 0/0 | 4 | 0 | 0 | 4 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| fribidi | tune | `68162babff` | 0/0 | 1 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| jansson | holdout | `684e18c927` | 0/0 | 2 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| libyaml | tune | `2c891fc7a7` | 0/0 | 4 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| re2 | tune | `6dcd83d60f` | 0/0 | 1 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| **Micro** | — | — | 312/258 | 106 | 32 | — | 975 | 20 | 0.051 | 0.058 | 0.000 | 0.021 | 0.150 | — |
| **Macro** | — | — | — | — | — | — | — | — | 0.030 | 0.033 | 0.000 | 0.019 | 0.124 | — |
The term “src sites” means source-file change sites in upstream base coordinates; “(non-test)” excludes test paths.

## Overall (micro)

Overall (micro): source-site recall 0.051 (16/312), non-test source-site recall 0.058 (15/258), build-site recall 0.000 (0/106), precision 0.021 (20/975), precision in patched files 0.150 (20/133).

Split tune (micro, 17 projects): source-site recall 0.052 (6/115), non-test source-site recall 0.060 (6/100), build-site recall 0.000 (0/48), precision 0.026 (10/384), precision in patched files 0.286 (10/35).
Split holdout (micro, 16 projects): source-site recall 0.051 (10/197), non-test source-site recall 0.057 (9/158), build-site recall 0.000 (0/58), precision 0.017 (10/591), precision in patched files 0.102 (10/98).

## Splits

Projects sorted by name using Python's case-sensitive string ordering alternate by index: even to tune, odd to holdout.

- Tune: asio, aws-c-common, c-ares, chrony, fribidi, gnutls, iperf3, libevent, libusb, libwebsockets, libyaml, lua, nghttp2, open-amp, re2, strongswan, unbound
- Holdout: avahi, aws-c-io, check, dlt-daemon, glog, googletest, jansson, libmetal, libuv, libxml2, lldpd, mosquitto, ntpsec, pistache, s2n-tls, tinyxml2

## Hits by rule

| rule_id | findings | TP findings | sites hit |
|---|---:|---:|---:|
| LNX-ACCEPT4 | 5 | 0 | 0 |
| LNX-EPOLL | 72 | 0 | 0 |
| LNX-EVENTFD | 24 | 0 | 0 |
| LNX-INOTIFY | 19 | 0 | 0 |
| LNX-LINK-FLAGS | 27 | 0 | 0 |
| LNX-LINK-FLAGS-OTHER | 1 | 0 | 0 |
| LNX-LINUX-HEADER | 180 | 5 | 3 |
| LNX-LINUX-IFDEF | 314 | 8 | 8 |
| LNX-PIPE2 | 9 | 0 | 0 |
| LNX-PRCTL | 26 | 1 | 2 |
| LNX-PROCFS | 79 | 1 | 1 |
| LNX-SENDFILE | 20 | 1 | 1 |
| LNX-SPLICE | 1 | 0 | 0 |
| LNX-SYSCALL | 154 | 4 | 3 |
| LNX-SYSINFO | 13 | 0 | 0 |
| LNX-TIMERFD | 31 | 0 | 0 |

## Runtime

| project | fetch seconds | scan seconds |
|---|---:|---:|
| asio | 0.003 | 14.834 |
| avahi | 0.003 | 3.196 |
| aws-c-io | 0.003 | 6.886 |
| c-ares | 0.004 | 3.910 |
| chrony | 0.004 | 3.143 |
| dlt-daemon | 0.004 | 23.960 |
| glog | 0.003 | 0.939 |
| gnutls | 0.003 | 19.633 |
| googletest | 0.004 | 8.602 |
| iperf3 | 0.003 | 1.197 |
| libevent | 0.003 | 5.038 |
| libmetal | 0.004 | 0.712 |
| libusb | 0.003 | 6.088 |
| libuv | 0.003 | 6.167 |
| libwebsockets | 0.003 | 788.220 |
| libxml2 | 0.017 | 94.053 |
| lldpd | 0.014 | 2.527 |
| lua | 0.011 | 1.755 |
| mosquitto | 0.016 | 4.244 |
| nghttp2 | 0.022 | 15.639 |
| ntpsec | 0.013 | 9.290 |
| open-amp | 0.010 | 0.469 |
| pistache | 0.011 | 14.490 |
| s2n-tls | 0.009 | 15.139 |
| strongswan | 0.015 | 44.283 |
| tinyxml2 | 0.016 | 0.715 |
| unbound | 0.013 | 17.061 |
| aws-c-common | 0.056 | 5.315 |
| check | 0.016 | 1.010 |
| fribidi | 0.015 | 0.678 |
| jansson | 0.011 | 0.593 |
| libyaml | 0.008 | 1.200 |
| re2 | 0.014 | 2.691 |
Total runtime: 0.0 seconds.

## Out of scope

- **asio**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **avahi**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 1.
- **aws-c-io**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 2; other-file change sites 0.
- **c-ares**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 17; other-file change sites 0.
- **chrony**: new files 3 (adjtime_qnx.h, sys_qnx.c, sys_qnx.h); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **dlt-daemon**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 1; mode-only 0; build-file change sites 14; other-file change sites 0.
- **glog**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 10; other-file change sites 0.
- **gnutls**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **googletest**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 9; other-file change sites 0.
- **iperf3**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **libevent**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **libmetal**: new files 31 (lib/system/qnx/CMakeLists.txt, lib/system/qnx/alloc.h, lib/system/qnx/assert.h, lib/system/qnx/cache.h, lib/system/qnx/condition.c); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 2; other-file change sites 0.
- **libusb**: new files 2 (libusb/os/nto_qnx_usbfs.c, libusb/os/nto_qnx_usbfs.h); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 7; other-file change sites 0.
- **libuv**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **libwebsockets**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **libxml2**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **lldpd**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **lua**: new files 1 (testes/libs/makefile.qnx); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 10.
- **mosquitto**: new files 7 (cmake/FindOpenSSL.cmake, test/broker/c/Makefile.qnx, test/broker/test_qnx.py, test/client/test_qnx.sh, test/lib/c/Makefile.qnx); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 2; other-file change sites 20.
- **nghttp2**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **ntpsec**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 4; other-file change sites 0.
- **open-amp**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **pistache**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 1.
- **s2n-tls**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **strongswan**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 7; other-file change sites 0.
- **tinyxml2**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **unbound**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **aws-c-common**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **check**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 4; other-file change sites 0.
- **fribidi**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **jansson**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 2; other-file change sites 0.
- **libyaml**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 4; other-file change sites 0.
- **re2**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.

See [METHOD.md](METHOD.md) for methodology.
