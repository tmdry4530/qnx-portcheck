#!/usr/bin/env bash
set -u
# shellcheck source=demo/scenes/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rm -rf /tmp/qnx-demo
mkdir -p /tmp/qnx-demo
show_cmd 'cp -a examples/linux-daemon /tmp/qnx-demo/linux-daemon'
show_cmd 'qnx-portcheck scaffold /tmp/qnx-demo/linux-daemon --dry-run'
show_cmd 'qnx-portcheck scaffold /tmp/qnx-demo/linux-daemon'
show_cmd 'ls /tmp/qnx-demo/linux-daemon/qnx/build'
show_cmd 'head -6 /tmp/qnx-demo/linux-daemon/qnx/build/common.mk'
sleep "${DEMO_PAUSE:-1.5}"
