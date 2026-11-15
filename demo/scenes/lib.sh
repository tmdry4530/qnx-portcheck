#!/usr/bin/env bash
# Shared deterministic terminal setup for scene recordings.
export PS1='$ '
export LC_ALL=C.UTF-8
export TZ=UTC
export COLUMNS=100
export LINES=28
repo_src="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/src"
export PYTHONPATH="$repo_src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1

show_cmd() {
    local command_text="$1"
    local success_note="${2:-}"
    local delay="${DEMO_TYPE_DELAY:-0.02}"
    local char_index
    printf '$ '
    for ((char_index = 0; char_index < ${#command_text}; char_index++)); do
        printf '%s' "${command_text:char_index:1}"
        if [[ "$delay" != 0 ]]; then sleep "$delay"; fi
    done
    printf '\n'
    local command_status=0
    eval "$command_text" || command_status=$?
    if [[ "${DEMO_SHOW_EXIT:-0}" == 1 ]]; then
        if ((command_status != 0)); then
            printf '(exit %s)\n' "$command_status"
        elif [[ -n "$success_note" ]]; then
            printf '(exit 0: %s)\n' "$success_note"
        else
            printf '(exit 0)\n'
        fi
    elif ((command_status != 0)); then
        printf '(exit %s)\n' "$command_status"
    fi
    sleep "${DEMO_PAUSE:-1.5}"
    return "$command_status"
}

qnx-portcheck() {
    if python3 -c 'import qnx_portcheck.cli' >/dev/null 2>&1; then
        python3 -c 'import sys; from qnx_portcheck.cli import main; sys.exit(main())' "$@"
        return $?
    fi
    case "${1:-}" in
        scaffold)
            shift
            python3 -m qnx_portcheck.scaffold scaffold "$@"
            ;;
        lint-buildfile)
            shift
            python3 -m qnx_portcheck.lint_buildfile lint-buildfile "$@"
            ;;
        scan)
            printf '%s\n' 'qnx-portcheck: scan CLI is not merged yet' >&2
            return 3
            ;;
        *)
            printf '%s\n' 'qnx-portcheck: CLI is not merged yet' >&2
            return 3
            ;;
    esac
}

has_scan_cli() {
    python3 -c 'import qnx_portcheck.cli' >/dev/null 2>&1
}
