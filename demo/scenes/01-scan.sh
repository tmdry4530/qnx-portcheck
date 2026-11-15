#!/usr/bin/env bash
set -u
# shellcheck source=demo/scenes/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
show_cmd 'qnx-portcheck scan examples/linux-daemon --format text'
sleep "${DEMO_PAUSE:-1.5}"
