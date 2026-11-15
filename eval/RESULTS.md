# qnx-portcheck evaluation results

Numbers below come from an actual run of qnx-portcheck on the upstream base commits listed in eval/projects.yaml, compared with the qnx-ports patches (see METHOD.md). The tool was not run on a QNX target.

- Label: REAL
- Date (KST): 2026-11-15T14:15:04.407845+09:00
- Window: ±3 lines
- Merge gap: 3 lines
- Scan command: `qnx-portcheck scan {path} --format json --fail-on never`
- Scanner: qnx-portcheck/0.1.0
- Harness version: 0.1.0
- Scanner source commit: 5118669
- Harness git SHA: 5118669
- Total runtime: 38.7 s
- Projects: 33
- Reused projects: 0
- Scan results generated (KST): 2026-11-15T14:14:25.685985+09:00 to 2026-11-15T14:15:04.013567+09:00

| project | split | upstream base | src sites (all/non-test) | build sites | other sites | new files | findings | TP | recall src | recall src non-test | recall build | precision | precision (patched files) | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| asio | tune | `814f67e730` | 14/8 | 0 | 0 | 0 | 95 | 3 | 0.214 | 0.125 | — | 0.032 | 0.250 | ok |
| avahi | holdout | `4294bbff57` | 3/3 | 1 | 1 | 0 | 40 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| aws-c-io | holdout | `bfb0819d39` | 11/11 | 2 | 0 | 0 | 44 | 2 | 0.182 | 0.182 | 0.000 | 0.045 | 0.118 | ok |
| c-ares | tune | `6508d6ad27` | 16/16 | 17 | 0 | 0 | 57 | 2 | 0.062 | 0.062 | 0.059 | 0.035 | 0.105 | ok |
| chrony | tune | `d622b222a9` | 11/8 | 3 | 0 | 3 | 31 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| dlt-daemon | holdout | `0f2d4cfffa` | 2/2 | 14 | 0 | 0 | 66 | 1 | 0.000 | 0.000 | 0.071 | 0.015 | 0.250 | ok |
| glog | holdout | `b33e3bad4c` | 27/14 | 10 | 0 | 0 | 40 | 4 | 0.111 | 0.214 | 0.000 | 0.100 | 0.167 | ok |
| gnutls | tune | `5dd9a55040` | 6/6 | 0 | 0 | 0 | 28 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| googletest | holdout | `b796f7d446` | 3/2 | 9 | 0 | 0 | 16 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| iperf3 | tune | `dfcea9f6a0` | 4/4 | 0 | 0 | 0 | 45 | 1 | 0.250 | 0.250 | — | 0.022 | 0.250 | ok |
| libevent | tune | `5df3037d10` | 1/1 | 1 | 0 | 0 | 69 | 1 | 1.000 | 1.000 | 0.000 | 0.015 | 1.000 | ok |
| libmetal | holdout | `f8a0e51aee` | 0/0 | 2 | 0 | 31 | 23 | 0 | — | — | 0.000 | 0.000 | — | ok |
| libusb | tune | `e782eeb251` | 4/4 | 7 | 0 | 2 | 45 | 3 | 0.000 | 0.000 | 0.143 | 0.067 | 0.158 | ok |
| libuv | holdout | `5152db2cbf` | 40/19 | 1 | 0 | 0 | 473 | 16 | 0.375 | 0.053 | 0.000 | 0.034 | 0.105 | ok |
| libwebsockets | tune | `fbb0baf6af` | 5/5 | 1 | 0 | 0 | 126 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| libxml2 | holdout | `de918d45e1` | 1/1 | 0 | 0 | 0 | 34 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| lldpd | holdout | `df8d729859` | 22/22 | 3 | 0 | 0 | 72 | 1 | 0.091 | 0.091 | 0.000 | 0.014 | 0.100 | ok |
| lua | tune | `cb88c1cd5d` | 5/5 | 0 | 10 | 1 | 1 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| mosquitto | holdout | `b0277869d9` | 0/0 | 2 | 20 | 7 | 49 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| nghttp2 | tune | `526ff38e02` | 1/1 | 3 | 0 | 0 | 18 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| ntpsec | holdout | `39b19ff71b` | 35/32 | 4 | 0 | 0 | 50 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | — | ok |
| open-amp | tune | `604cdf9a45` | 4/4 | 0 | 0 | 0 | 1 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| pistache | holdout | `ddffda861a` | 19/18 | 3 | 1 | 0 | 81 | 11 | 0.526 | 0.500 | 0.000 | 0.136 | 0.458 | ok |
| s2n-tls | holdout | `a7862238a9` | 32/32 | 1 | 0 | 0 | 81 | 25 | 0.719 | 0.719 | 1.000 | 0.309 | 0.641 | ok |
| strongswan | tune | `4d709df8b2` | 23/22 | 7 | 0 | 0 | 130 | 5 | 0.217 | 0.227 | 0.000 | 0.038 | 0.156 | ok |
| tinyxml2 | holdout | `321ea883b7` | 2/2 | 0 | 0 | 0 | 3 | 1 | 0.500 | 0.500 | — | 0.333 | 1.000 | ok |
| unbound | tune | `a33f0638e1` | 21/16 | 0 | 0 | 0 | 55 | 10 | 0.333 | 0.375 | — | 0.182 | 0.476 | ok |
| aws-c-common | tune | `2b67a658e4` | 0/0 | 3 | 0 | 0 | 51 | 2 | — | — | 0.667 | 0.039 | 0.200 | ok |
| check | holdout | `11970a7e11` | 0/0 | 4 | 0 | 0 | 16 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| fribidi | tune | `68162babff` | 0/0 | 1 | 0 | 0 | 4 | 0 | — | — | 0.000 | 0.000 | — | ok |
| jansson | holdout | `684e18c927` | 0/0 | 2 | 0 | 0 | 1 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| libyaml | tune | `2c891fc7a7` | 0/0 | 4 | 0 | 0 | 0 | 0 | — | — | 0.000 | — | — | ok |
| re2 | tune | `6dcd83d60f` | 0/0 | 1 | 0 | 0 | 5 | 0 | — | — | 0.000 | 0.000 | 0.000 | ok |
| **Micro** | — | — | 312/258 | 106 | 32 | — | 1850 | 88 | 0.237 | 0.217 | 0.057 | 0.048 | 0.214 | — |
| **Macro** | — | — | — | — | — | — | — | — | 0.183 | 0.172 | 0.078 | 0.044 | 0.226 | — |
The term “src sites” means source-file change sites in upstream base coordinates; “(non-test)” excludes test paths.

## Overall (micro)

Overall (micro): source-site recall 0.237 (74/312), non-test source-site recall 0.217 (56/258), build-site recall 0.057 (6/106), precision 0.048 (88/1850), precision in patched files 0.214 (88/411).

Split tune (micro, 17 projects): source-site recall 0.157 (18/115), non-test source-site recall 0.150 (15/100), build-site recall 0.083 (4/48), precision 0.035 (27/761), precision in patched files 0.206 (27/131).
Split holdout (micro, 16 projects): source-site recall 0.284 (56/197), non-test source-site recall 0.260 (41/158), build-site recall 0.035 (2/58), precision 0.056 (61/1089), precision in patched files 0.218 (61/280).

## Splits

Projects sorted by name using Python's case-sensitive string ordering alternate by index: even to tune, odd to holdout.

- Tune: asio, aws-c-common, c-ares, chrony, fribidi, gnutls, iperf3, libevent, libusb, libwebsockets, libyaml, lua, nghttp2, open-amp, re2, strongswan, unbound
- Holdout: avahi, aws-c-io, check, dlt-daemon, glog, googletest, jansson, libmetal, libuv, libxml2, lldpd, mosquitto, ntpsec, pistache, s2n-tls, tinyxml2

## Hits by rule

| rule_id | findings | TP findings | sites hit |
|---|---:|---:|---:|
| BLD-AUTOCONF-HOST | 99 | 4 | 2 |
| BLD-CMAKE-PLATFORM | 152 | 5 | 4 |
| LNX-ACCEPT4 | 5 | 0 | 0 |
| LNX-EPOLL | 46 | 0 | 0 |
| LNX-EVENTFD | 13 | 0 | 0 |
| LNX-INOTIFY | 6 | 0 | 0 |
| LNX-LINK-FLAGS | 31 | 0 | 0 |
| LNX-LINK-FLAGS-OTHER | 2 | 0 | 0 |
| LNX-LINUX-HEADER | 161 | 3 | 2 |
| LNX-LINUX-IFDEF | 314 | 8 | 8 |
| LNX-PIPE2 | 9 | 0 | 0 |
| LNX-PRCTL | 22 | 1 | 2 |
| LNX-PROCFS | 70 | 1 | 1 |
| LNX-SENDFILE | 15 | 0 | 0 |
| LNX-SPLICE | 1 | 0 | 0 |
| LNX-SYSCALL | 138 | 4 | 3 |
| LNX-SYSINFO | 12 | 0 | 0 |
| LNX-TIMERFD | 17 | 0 | 0 |
| PORT-MINMAX | 51 | 23 | 23 |
| PORT-MINMAX-DEFINE | 9 | 2 | 2 |
| PORT-OS-IFDEF | 618 | 29 | 27 |
| PORT-QNXNTO | 7 | 2 | 2 |
| PORT-SA-RESTART | 12 | 2 | 2 |
| PORT-TIMEVAL | 40 | 4 | 4 |

## Runtime

| project | fetch seconds | scan seconds |
|---|---:|---:|
| asio | 0.003 | 2.454 |
| avahi | 0.003 | 0.656 |
| aws-c-io | 0.003 | 0.713 |
| c-ares | 0.003 | 0.691 |
| chrony | 0.003 | 0.552 |
| dlt-daemon | 0.003 | 1.032 |
| glog | 0.003 | 0.228 |
| gnutls | 0.003 | 3.281 |
| googletest | 0.003 | 0.995 |
| iperf3 | 0.003 | 0.204 |
| libevent | 0.003 | 0.850 |
| libmetal | 0.004 | 0.329 |
| libusb | 0.003 | 0.591 |
| libuv | 0.003 | 1.030 |
| libwebsockets | 0.003 | 5.786 |
| libxml2 | 0.004 | 2.458 |
| lldpd | 0.004 | 0.543 |
| lua | 0.004 | 0.349 |
| mosquitto | 0.003 | 0.739 |
| nghttp2 | 0.003 | 1.458 |
| ntpsec | 0.003 | 0.879 |
| open-amp | 0.003 | 0.144 |
| pistache | 0.003 | 0.608 |
| s2n-tls | 0.003 | 2.379 |
| strongswan | 0.003 | 5.177 |
| tinyxml2 | 0.003 | 0.126 |
| unbound | 0.003 | 2.017 |
| aws-c-common | 0.003 | 0.877 |
| check | 0.003 | 0.224 |
| fribidi | 0.003 | 0.191 |
| jansson | 0.003 | 0.174 |
| libyaml | 0.003 | 0.211 |
| re2 | 0.003 | 0.387 |
Total runtime: 38.7 seconds.

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
