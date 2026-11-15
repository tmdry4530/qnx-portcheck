> **FAKE-SCAN harness smoke results — produced with eval/fake_scan.py, NOT qnx-portcheck. These numbers only show the harness works end-to-end; they are NOT real metrics.**

# qnx-portcheck evaluation results

- Label: FAKE-SCAN
- Date (KST): 2026-11-15T12:34:24.768435+09:00
- Window: ±3 lines
- Merge gap: 3 lines
- Scan command: `python3 eval/fake_scan.py scan {path} --format json`
- Scanner: fake-scan/0.0.0-fake
- Harness version: 0.1.0
- Scanner source commit: af18fa6
- Harness git SHA: 5acf9d0
- Total runtime: 7.0 s
- Projects: 33

| project | upstream base | src sites (all/non-test) | build sites | other sites | new files | findings | TP | recall src | recall src non-test | recall build | precision | precision (patched files) | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| asio | `814f67e730` | 14/8 | 0 | 0 | 0 | 202 | 0 | 0.000 | 0.000 | — | 0.000 | 0.000 | ok |
| avahi | `4294bbff57` | 3/3 | 1 | 1 | 0 | 61 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| aws-c-io | `bfb0819d39` | 11/11 | 2 | 0 | 0 | 472 | 1 | 0.091 | 0.091 | 0.000 | 0.002 | 0.007 | ok |
| c-ares | `6508d6ad27` | 16/16 | 17 | 0 | 0 | 77 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| chrony | `d622b222a9` | 11/8 | 3 | 0 | 3 | 26 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| dlt-daemon | `0f2d4cfffa` | 2/2 | 14 | 0 | 0 | 50 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| glog | `b33e3bad4c` | 27/14 | 10 | 0 | 0 | 19 | 2 | 0.074 | 0.143 | 0.000 | 0.105 | 0.125 | ok |
| gnutls | `5dd9a55040` | 6/6 | 0 | 0 | 0 | 23 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| googletest | `b796f7d446` | 3/2 | 9 | 0 | 0 | 2 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| iperf3 | `dfcea9f6a0` | 4/4 | 0 | 0 | 0 | 28 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| libevent | `5df3037d10` | 1/1 | 1 | 0 | 0 | 111 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| libmetal | `f8a0e51aee` | 0/0 | 2 | 0 | 31 | 34 | 0 | — | — | 0.000 | 0.000 | — | ok |
| libusb | `e782eeb251` | 4/4 | 7 | 0 | 2 | 30 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| libuv | `5152db2cbf` | 40/19 | 1 | 0 | 0 | 289 | 6 | 0.150 | 0.316 | 0.000 | 0.021 | 0.091 | ok |
| libwebsockets | `fbb0baf6af` | 5/5 | 1 | 0 | 0 | 174 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| libxml2 | `de918d45e1` | 1/1 | 0 | 0 | 0 | 4 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| lldpd | `df8d729859` | 22/22 | 3 | 0 | 0 | 65 | 1 | 0.091 | 0.091 | 0.000 | 0.015 | 0.333 | ok |
| lua | `cb88c1cd5d` | 5/5 | 0 | 10 | 1 | 1 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| mosquitto | `b0277869d9` | 0/0 | 2 | 20 | 7 | 62 | 0 | — | — | 0.000 | 0.000 | — | ok |
| nghttp2 | `526ff38e02` | 1/1 | 3 | 0 | 0 | 15 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| ntpsec | `39b19ff71b` | 35/32 | 4 | 0 | 0 | 16 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| open-amp | `604cdf9a45` | 4/4 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | — | — | — | ok |
| pistache | `ddffda861a` | 19/18 | 3 | 1 | 0 | 272 | 6 | 0.316 | 0.278 | 0.000 | 0.022 | 0.043 | ok |
| s2n-tls | `a7862238a9` | 32/32 | 1 | 0 | 0 | 30 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| strongswan | `4d709df8b2` | 23/22 | 7 | 0 | 0 | 101 | 5 | 0.130 | 0.136 | 0.000 | 0.050 | 0.217 | ok |
| tinyxml2 | `321ea883b7` | 2/2 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 | — | — | — | ok |
| unbound | `a33f0638e1` | 21/16 | 0 | 0 | 0 | 73 | 3 | 0.095 | 0.125 | — | 0.041 | 1.000 | ok |
| aws-c-common | `2b67a658e4` | 0/0 | 3 | 0 | 0 | 16 | 0 | — | — | 0.000 | 0.000 | — | ok |
| check | `11970a7e11` | 0/0 | 4 | 0 | 0 | 9 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| fribidi | `68162babff` | 0/0 | 1 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| jansson | `684e18c927` | 0/0 | 2 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| libyaml | `2c891fc7a7` | 0/0 | 4 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| re2 | `6dcd83d60f` | 0/0 | 1 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| **Micro** | — | 312/258 | 106 | 32 | — | 2262 | 24 | 0.070 | 0.081 | 0.000 | 0.011 | 0.054 | — |

## Overall (micro)

Overall (micro): source-site recall 0.070 (22/312), non-test source-site recall 0.081 (21/258), build-site recall 0.000 (0/106), precision 0.011 (24/2262), precision in patched files 0.054 (24/442).

## Hits by rule

| rule_id | findings | TP findings | sites hit |
|---|---:|---:|---:|
| FAKE-CMAKE-SYSTEM-NAME-STREQUAL-LINUX | 6 | 0 | 0 |
| FAKE-EPOLL | 949 | 1 | 1 |
| FAKE-EVENTFD | 178 | 0 | 0 |
| FAKE-INOTIFY | 82 | 0 | 0 |
| FAKE-LDL | 75 | 0 | 0 |
| FAKE-LINUX | 595 | 20 | 17 |
| FAKE-LPTHREAD | 84 | 0 | 0 |
| FAKE-LRT | 13 | 0 | 0 |
| FAKE-MSG-NOSIGNAL | 54 | 0 | 0 |
| FAKE-PRCTL | 31 | 1 | 2 |
| FAKE-PROC-SELF | 47 | 2 | 2 |
| FAKE-PTHREAD-SETNAME-NP | 15 | 0 | 0 |
| FAKE-SCHED-SETAFFINITY | 4 | 0 | 0 |
| FAKE-SIGNALFD | 2 | 0 | 0 |
| FAKE-SOCK-CLOEXEC | 43 | 0 | 0 |
| FAKE-SYS-EPOLL-H | 11 | 0 | 0 |
| FAKE-SYS-SYSINFO-H | 5 | 0 | 0 |
| FAKE-TIMERFD | 68 | 0 | 0 |

## Runtime

| project | fetch seconds | scan seconds |
|---|---:|---:|
| asio | 0.003 | 0.383 |
| avahi | 0.003 | 0.128 |
| aws-c-io | 0.003 | 0.121 |
| c-ares | 0.003 | 0.132 |
| chrony | 0.003 | 0.117 |
| dlt-daemon | 0.003 | 0.157 |
| glog | 0.003 | 0.070 |
| gnutls | 0.003 | 0.620 |
| googletest | 0.003 | 0.139 |
| iperf3 | 0.003 | 0.072 |
| libevent | 0.003 | 0.135 |
| libmetal | 0.003 | 0.081 |
| libusb | 0.003 | 0.091 |
| libuv | 0.003 | 0.166 |
| libwebsockets | 0.003 | 0.505 |
| libxml2 | 0.003 | 0.385 |
| lldpd | 0.003 | 0.104 |
| lua | 0.003 | 0.076 |
| mosquitto | 0.003 | 0.144 |
| nghttp2 | 0.004 | 0.244 |
| ntpsec | 0.004 | 0.158 |
| open-amp | 0.003 | 0.056 |
| pistache | 0.003 | 0.118 |
| s2n-tls | 0.003 | 0.507 |
| strongswan | 0.003 | 1.041 |
| tinyxml2 | 0.003 | 0.057 |
| unbound | 0.003 | 0.294 |
| aws-c-common | 0.003 | 0.180 |
| check | 0.003 | 0.071 |
| fribidi | 0.003 | 0.060 |
| jansson | 0.003 | 0.066 |
| libyaml | 0.003 | 0.064 |
| re2 | 0.003 | 0.083 |
Total runtime: 7.0 seconds.
| **Macro** | — | — | — | — | — | — | — | 0.038 | 0.047 | 0.000 | 0.009 | 0.107 | — |

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

The term “src sites” means source-file change sites in upstream base coordinates; “(non-test)” excludes test paths.

See [METHOD.md](METHOD.md) for methodology.
