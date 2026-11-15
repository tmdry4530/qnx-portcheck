# qnx-portcheck

Host-side tool for Linux to QNX 8.0 porting. It is a host tool and never runs on a QNX target.

## scan

Run `qnx-portcheck scan <path>` to inspect C/C++ sources and build files. Choose `--format text`, `json`, or `sarif`; use `--out FILE` to write a report and `--fail-on error|warning|note|never` to set the exit threshold.

| Rule | Default severity | QNX documentation |
|---|---|---|
| LNX-EPOLL | warning | yes |
| LNX-INOTIFY | note | yes |
| LNX-EVENTFD | warning | yes |
| LNX-TIMERFD | warning | yes |
| LNX-SIGNALFD | warning | yes |
| LNX-PRCTL | error | yes |
| LNX-SYSINFO | error | no |
| LNX-SENDFILE | error | no |
| LNX-SPLICE | error | no |
| LNX-ACCEPT4 | note | yes |
| LNX-PIPE2 | note | yes |
| LNX-SYSCALL | error | no |
| LNX-LINUX-HEADER | error | no |
| LNX-PROCFS | warning | yes |
| LNX-LINUX-IFDEF | warning | yes |
| LNX-LINK-FLAGS | warning | yes |
| LNX-LINK-FLAGS-OTHER | warning | no |
