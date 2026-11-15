# qnx-portcheck evaluation results

Numbers below come from an actual run of qnx-portcheck on the upstream base commits listed in eval/projects.yaml, compared with the qnx-ports patches (see METHOD.md). The tool was not run on a QNX target.

- Label: REAL
- Date (KST): 2026-11-15T15:09:25.651404+09:00
- Window: ±3 lines
- Merge gap: 3 lines
- Scan command: `python -m qnx_portcheck scan {path} --format json --fail-on never`
- Scanner: qnx-portcheck/0.1.0
- Harness version: 0.1.0
- Scanner source commit: 5118669
- Harness git SHA: 8ce088a
- Total runtime: 0.0 s
- Projects: 33
- Fresh projects: 15
- Reused projects: 48
- Scan results generated (KST): 2026-11-15T14:46:13.993389+09:00 to 2026-11-15T14:52:31.912269+09:00

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

## Fresh projects

| project | split | upstream base | src sites (all/non-test) | build sites | other sites | new files | findings | TP | recall src | recall src non-test | recall build | precision | precision (patched files) | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AMQP-CPP | fresh | `ca49382bfc` | 1/1 | 3 | 0 | 0 | 16 | 6 | 0.000 | 0.000 | 1.000 | 0.375 | 1.000 | ok |
| CANdb | fresh | `150c42a8cd` | 2/0 | 5 | 5 | 0 | 2 | 0 | 0.000 | — | 0.000 | 0.000 | — | ok |
| Catch2 | fresh | `4e8d92bf02` | 4/4 | 3 | 0 | 0 | 12 | 1 | 0.250 | 0.250 | 0.000 | 0.083 | 0.333 | ok |
| EmulationStation | fresh | `51b6f4162d` | 31/31 | 3 | 0 | 0 | 32 | 2 | 0.032 | 0.032 | 0.333 | 0.062 | 0.400 | ok |
| Fast-CDR | fresh | `455a4e7e62` | 2/0 | 8 | 1 | 0 | 4 | 0 | 0.000 | — | 0.000 | 0.000 | — | ok |
| Fast-DDS | fresh | `7606b96087` | 12/2 | 13 | 10 | 3 | 300 | 5 | 0.333 | 0.000 | 0.077 | 0.017 | 0.417 | ok |
| OpenBLAS | fresh | `5ef8b19646` | 12/12 | 15 | 0 | 0 | 224 | 5 | 0.000 | 0.000 | 0.333 | 0.022 | 0.172 | ok |
| SDL | fresh | `4cd981609b` | 41/41 | 1790 | 0 | 11 | 289 | 7 | 0.073 | 0.073 | 0.000 | 0.024 | 0.063 | ok |
| abseil-cpp | fresh | `b014bff59d` | 8/4 | 1 | 0 | 0 | 147 | 3 | 0.375 | 0.500 | 0.000 | 0.020 | 0.250 | ok |
| abuild | fresh | `1355cc9b63` | 1/1 | 0 | 27 | 0 | 1 | 0 | 0.000 | 0.000 | — | 0.000 | — | ok |
| apk-tools | fresh | `9331888de6` | 12/12 | 0 | 0 | 0 | 23 | 5 | 0.500 | 0.500 | — | 0.217 | 0.714 | ok |
| azure-iot-sdk-c | fresh | `9c70f98b7b` | 2/2 | 2 | 0 | 0 | 160 | 4 | 1.000 | 1.000 | 1.000 | 0.025 | 0.571 | ok |
| benchmark | fresh | `344117638c` | 2/1 | 6 | 0 | 11 | 13 | 0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | ok |
| capnproto | fresh | `1a0e12c0a3` | 22/9 | 9 | 0 | 0 | 29 | 3 | 0.000 | 0.000 | 0.222 | 0.103 | 0.750 | ok |
| cpuinfo | fresh | `3c8b1533ac` | 140/140 | 6 | 0 | 2 | 196 | 7 | 0.021 | 0.021 | 0.500 | 0.036 | 0.143 | ok |
| **Micro** | — | — | 292/260 | 1864 | 43 | — | 1448 | 48 | 0.079 | 0.069 | 0.009 | 0.033 | 0.191 | — |
| **Macro** | — | — | — | — | — | — | — | — | 0.172 | 0.183 | 0.267 | 0.066 | 0.401 | — |
The term “src sites” means source-file change sites in upstream base coordinates; “(non-test)” excludes test paths.

## Overall (micro)

Overall (micro): source-site recall 0.237 (74/312), non-test source-site recall 0.217 (56/258), build-site recall 0.057 (6/106), precision 0.048 (88/1850), precision in patched files 0.214 (88/411).

Split tune (micro, 17 projects): source-site recall 0.157 (18/115), non-test source-site recall 0.150 (15/100), build-site recall 0.083 (4/48), precision 0.035 (27/761), precision in patched files 0.206 (27/131).
Split holdout (seen during tuning) (micro, 16 projects): source-site recall 0.284 (56/197), non-test source-site recall 0.260 (41/158), build-site recall 0.035 (2/58), precision 0.056 (61/1089), precision in patched files 0.218 (61/280).
Split fresh (micro, 15 projects): source-site recall 0.079 (23/292), non-test source-site recall 0.069 (18/260), build-site recall 0.009 (17/1864), precision 0.033 (48/1448), precision in patched files 0.191 (48/251).

## Splits

Original projects (entries without split) sorted by name using Python's case-sensitive string ordering alternate by index: even to tune, odd to holdout. Fresh projects are selected later by the committed criteria in METHOD.md and never shift tune/holdout.

- Tune: asio, aws-c-common, c-ares, chrony, fribidi, gnutls, iperf3, libevent, libusb, libwebsockets, libyaml, lua, nghttp2, open-amp, re2, strongswan, unbound
- Holdout (seen during tuning): avahi, aws-c-io, check, dlt-daemon, glog, googletest, jansson, libmetal, libuv, libxml2, lldpd, mosquitto, ntpsec, pistache, s2n-tls, tinyxml2
- Fresh projects: AMQP-CPP, CANdb, Catch2, EmulationStation, Fast-CDR, Fast-DDS, OpenBLAS, SDL, abseil-cpp, abuild, apk-tools, azure-iot-sdk-c, benchmark, capnproto, cpuinfo

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

## Hits by rule (fresh)

| rule_id | findings | TP findings | sites hit |
|---|---:|---:|---:|
| BLD-AUTOCONF-HOST | 45 | 0 | 0 |
| BLD-CMAKE-PLATFORM | 286 | 9 | 9 |
| LNX-INOTIFY | 6 | 0 | 0 |
| LNX-LINK-FLAGS | 145 | 12 | 9 |
| LNX-LINUX-HEADER | 41 | 0 | 0 |
| LNX-LINUX-IFDEF | 187 | 4 | 4 |
| LNX-PIPE2 | 7 | 0 | 0 |
| LNX-PROCFS | 149 | 4 | 1 |
| LNX-SPLICE | 16 | 0 | 0 |
| LNX-SYSCALL | 66 | 0 | 0 |
| LNX-SYSINFO | 7 | 0 | 0 |
| PORT-MINMAX-DEFINE | 4 | 0 | 0 |
| PORT-OS-IFDEF | 468 | 17 | 18 |
| PORT-QNXNTO | 21 | 2 | 2 |

## Runtime

| project | fetch seconds | scan seconds |
|---|---:|---:|
| asio | 7.416 | 2.453 |
| avahi | 5.179 | 0.648 |
| aws-c-io | 6.140 | 0.705 |
| c-ares | 5.427 | 0.689 |
| chrony | 5.796 | 0.544 |
| dlt-daemon | 6.024 | 1.068 |
| glog | 4.129 | 0.230 |
| gnutls | 8.630 | 3.306 |
| googletest | 6.482 | 1.008 |
| iperf3 | 6.001 | 0.213 |
| libevent | 5.367 | 0.856 |
| libmetal | 4.272 | 0.245 |
| libusb | 5.571 | 0.585 |
| libuv | 6.626 | 1.037 |
| libwebsockets | 6.947 | 5.896 |
| libxml2 | 7.204 | 2.437 |
| lldpd | 5.948 | 0.529 |
| lua | 3.696 | 0.344 |
| mosquitto | 5.274 | 0.706 |
| nghttp2 | 4.595 | 1.356 |
| ntpsec | 5.695 | 0.874 |
| open-amp | 5.009 | 0.144 |
| pistache | 4.874 | 0.611 |
| s2n-tls | 7.288 | 2.396 |
| strongswan | 8.462 | 5.170 |
| tinyxml2 | 5.926 | 0.129 |
| unbound | 6.372 | 2.021 |
| aws-c-common | 5.117 | 0.858 |
| check | 5.218 | 0.225 |
| fribidi | 7.177 | 0.195 |
| jansson | 4.672 | 0.170 |
| libyaml | 4.622 | 0.199 |
| re2 | 5.682 | 0.387 |
| AMQP-CPP (fresh) | 5.009 | 0.348 |
| CANdb (fresh) | 4.983 | 0.092 |
| Catch2 (fresh) | 6.544 | 0.821 |
| EmulationStation (fresh) | 5.213 | 0.428 |
| Fast-CDR (fresh) | 7.158 | 0.511 |
| Fast-DDS (fresh) | 8.179 | 11.865 |
| OpenBLAS (fresh) | 12.177 | 31.652 |
| SDL (fresh) | 5.780 | 5.276 |
| abseil-cpp (fresh) | 5.558 | 2.960 |
| abuild (fresh) | 4.875 | 0.058 |
| apk-tools (fresh) | 5.286 | 0.301 |
| azure-iot-sdk-c (fresh) | 6.968 | 3.014 |
| benchmark (fresh) | 4.276 | 0.247 |
| capnproto (fresh) | 4.591 | 0.879 |
| cpuinfo (fresh) | 6.207 | 2.255 |
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
- **AMQP-CPP (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **CANdb (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 5; other-file change sites 5.
- **Catch2 (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **EmulationStation (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 3; other-file change sites 0.
- **Fast-CDR (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 8; other-file change sites 1.
- **Fast-DDS (fresh)**: new files 3 (build_qnx/README.md, build_qnx/project_hooks.cmake, qnx_patches/Fast-DDS.patch); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 13; other-file change sites 10.
- **OpenBLAS (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 15; other-file change sites 0.
- **SDL (fresh)**: new files 11 (.gitignore, include/SDL_config_qnx.h, src/audio/qsa/qsa_struct.h, src/audio/qsa/qsa_symbol_list.h, src/video/qnx/qnx_joystick.c); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1790; other-file change sites 0.
- **abseil-cpp (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 1; other-file change sites 0.
- **abuild (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 27.
- **apk-tools (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 0; other-file change sites 0.
- **azure-iot-sdk-c (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 2; other-file change sites 0.
- **benchmark (fresh)**: new files 11 (qnx/.gitignore, qnx/LICENSE.md, qnx/README.md, qnx/build/Makefile, qnx/build/common.mk); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 6; other-file change sites 0.
- **capnproto (fresh)**: new files 0 (); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 9; other-file change sites 0.
- **cpuinfo (fresh)**: new files 2 (src/qnx/api.c, src/qnx/api.h); rename-only 0; deleted-empty 0; binary 0; submodule 0; mode-only 0; build-file change sites 6; other-file change sites 0.

See [METHOD.md](METHOD.md) for methodology.
