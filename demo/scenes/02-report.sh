#!/usr/bin/env bash
set -u
# shellcheck source=demo/scenes/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
mkdir -p /tmp/qnx-demo >/dev/null 2>&1
show_cmd 'qnx-portcheck scan examples/linux-daemon --format json'
show_cmd 'qnx-portcheck scan examples/linux-daemon --format sarif --out /tmp/qnx-demo/demo.sarif'
show_cmd 'python3 -m json.tool /tmp/qnx-demo/demo.sarif | head -20'
sleep "${DEMO_PAUSE:-1.5}"
