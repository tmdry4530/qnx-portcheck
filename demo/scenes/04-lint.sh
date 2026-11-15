#!/usr/bin/env bash
set -u
# shellcheck source=demo/scenes/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
export DEMO_SHOW_EXIT=1
show_cmd 'qnx-portcheck lint-buildfile examples/linux-daemon/qnx/filewatchd.build' 'no diagnostics'
show_cmd 'qnx-portcheck lint-buildfile tests/fixtures/buildfiles/bad/multiple.build' || true
sleep "${DEMO_PAUSE:-1.5}"
