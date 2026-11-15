"""Focused checks for QNX platform portability rules."""
from pathlib import Path
from qnx_portcheck.rules import RULES_BY_ID
from qnx_portcheck.rules.base import SourceContext
from qnx_portcheck.scanner import _is_build
from qnx_portcheck.rules.guards import linux_only_lines

def context(text, path='x.c'):
    from qnx_portcheck.lexer import lex
    code, strings, comments = lex(text)
    return SourceContext(path, text, comments, code, strings, text.splitlines())

def hits(rule, text, path='x.c'):
    return list(RULES_BY_ID[rule].detector(context(text,path)))

def test_os_ifdef_precise_and_continued():
    assert hits('PORT-OS-IFDEF', '#if defined(__APPLE_CC__)\n') == []
    assert hits('PORT-OS-IFDEF', '#if defined(__APPLE__) && \\\n defined(__MACH__)\n') [0].line == 1
    assert not hits('PORT-OS-IFDEF', '#if defined(__APPLE__) || defined(__QNX__)\n')

def test_qnxnto_minmax_timeval_and_restart():
    assert hits('PORT-QNXNTO','#ifdef __QNXNTO__\n')
    assert not hits('PORT-QNXNTO','#if defined(__QNXNTO__) && defined(__QNX__)\n')
    assert not hits('PORT-MINMAX','int a = MIN(1,2);')
    assert hits('PORT-MINMAX','#include <sys/param.h>\nint a=MIN(1,2);')[0].line == 1
    assert not hits('PORT-MINMAX','#include <sys/param.h>\n#define MIN(a,b) 1\nint a=MIN(1,2);')
    assert not hits('PORT-MINMAX-DEFINE','#ifndef min\n#define min(a,b) 1\n#endif')
    assert hits('PORT-SA-RESTART','int x=SA_RESTART;')
    assert hits('PORT-SA-RESTART','#define X SA_RESTART')
    assert not hits('PORT-SA-RESTART','#ifdef SA_RESTART\nint x=SA_RESTART;')
    assert not hits('PORT-TIMEVAL','#include <sys/time.h>\nstruct timeval x;', 'x.h')
    assert hits('PORT-TIMEVAL','#include <stdio.h>\nstruct timeval x;', 'x.h')[0].line == 1
    assert not hits('PORT-TIMEVAL','#include <stdio.h>\nstruct timeval x;', 'x.c')  # headers only

def test_build_platform_and_discovery():
    assert hits('BLD-CMAKE-PLATFORM','if(APPLE)\nendif()','CMakeLists.txt')
    assert not hits('BLD-CMAKE-PLATFORM','if(APPLE)\nelseif(QNX)\nendif()','CMakeLists.txt')
    assert not hits('BLD-CMAKE-PLATFORM','if(WIN32)\nendif()','CMakeLists.txt')
    assert hits('BLD-AUTOCONF-HOST','case $host in\n *-linux*) ;;\n *-darwin*) ;;\nesac','configure.ac')
    assert not hits('BLD-AUTOCONF-HOST','case $host in\n *-nto-qnx*) ;;\nesac','configure.ac')
    assert _is_build(Path('configure.ac')) and _is_build(Path('os.m4'))
    assert not _is_build(Path('libtool.m4')) and not _is_build(Path('ax_foo.m4'))

def test_linux_guard_ranges():
    text = '#ifdef __linux__\nint a;\n#endif\n#ifndef __linux__\nint b;\n#else\nint c;\n'
    assert linux_only_lines(text) == frozenset({2, 7})
    assert not linux_only_lines('#if defined(__linux__) || defined(__APPLE__)\nint a;\n#endif')
    assert linux_only_lines('#if defined(__linux__) && X\nint a;\n#endif') == frozenset({2})
    assert linux_only_lines('#endif\nint x;') == frozenset()


def scan_text(tmp_path, name, text):
    from qnx_portcheck.scanner import scan
    path = tmp_path / name
    path.write_text(text)
    return [(f.rule_id, f.line) for f in scan(path).findings]


def test_minmax_location_is_last_include_before_first_use():
    text = '#include <sys/param.h>\n#include "a.h"\n\nint f(void) { return MAX(1, 2); }\n#include "late.h"\n'
    assert [h.line for h in hits('PORT-MINMAX', text)] == [2]


def test_minmax_define_unguarded_fires():
    assert [h.line for h in hits('PORT-MINMAX-DEFINE', '#define max(a,b) ((a)>(b)?(a):(b))\n')] == [1]
    assert not hits('PORT-MINMAX-DEFINE', '#if !defined(max)\n#define max(a,b) a\n#endif\n')
    assert hits('PORT-MINMAX-DEFINE', '#ifndef min\n#define max(a,b) a\n#endif\n')  # guard is per name


def test_linux_guard_drops_api_findings_but_keeps_the_guard(tmp_path):
    text = ('#ifdef __linux__\n#include <sys/epoll.h>\nint a = epoll_create1(0);\n#endif\n'
            '#if defined(__linux__) || defined(__APPLE__)\nint b = epoll_create1(0);\n#endif\n')
    found = scan_text(tmp_path, 'g.c', text)
    assert ('LNX-LINUX-IFDEF', 1) in found and ('LNX-LINUX-IFDEF', 5) in found
    assert ('LNX-EPOLL', 6) in found
    assert ('LNX-EPOLL', 2) not in found and ('LNX-EPOLL', 3) not in found


def test_feature_probe_guard_drops_facility_findings(tmp_path):
    text = ('#ifdef HAVE_SYS_EPOLL_H\n#include <sys/epoll.h>\n#endif\n'
            '#if defined(EVENT__HAVE_EPOLL) && !defined(X)\nint a = epoll_create(1);\n#else\nint b = epoll_create(1);\n#endif\n'
            '#ifndef HAVE_EPOLL\nint c = epoll_create(1);\n#endif\n'
            '#ifdef USBI_TIMERFD_AVAILABLE\nint d = epoll_create(1);\nint e = timerfd_create(0, 0);\n#endif\n')
    found = scan_text(tmp_path, 'f.c', text)
    epoll = sorted(line for rule, line in found if rule == 'LNX-EPOLL')
    assert epoll == [7, 10, 13]   # #else branch, #ifndef branch, other facility's guard
    assert not [line for rule, line in found if rule == 'LNX-TIMERFD']


def test_cmake_multiline_and_not_qnx():
    text = 'if(UNIX AND NOT APPLE\n   AND NOT CMAKE_SYSTEM_NAME MATCHES FreeBSD)\nendif()\n'
    assert [h.line for h in hits('BLD-CMAKE-PLATFORM', text, 'CMakeLists.txt')] == [1]
    assert not hits('BLD-CMAKE-PLATFORM', 'if(APPLE AND NOT QNX)\nendif()\n', 'CMakeLists.txt')
    nested = 'if(APPLE)\n  if(QNX)\n  endif()\nelseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")\nendif()\n'
    assert [h.line for h in hits('BLD-CMAKE-PLATFORM', nested, 'CMakeLists.txt')] == [1, 4]


def test_autoconf_as_case_and_dnl():
    text = 'AS_CASE([$host_os],\n  [linux*], [x=1],\n  [darwin*], [x=2])\n'
    assert [h.line for h in hits('BLD-AUTOCONF-HOST', text, 'configure.ac')] == [2, 3]
    commented = 'dnl case $host in\ndnl  *-linux*) ;;\ndnl esac\n'
    assert not hits('BLD-AUTOCONF-HOST', commented, 'configure.ac')


def test_autoconf_discovery_skips_generated_and_third_party_m4():
    for name in ('aclocal.m4', 'acx_pthread.m4', 'lib-prefix.m4', 'ltoptions.m4', 'pkg.m4'):
        assert not _is_build(Path(name)), name
    assert _is_build(Path('configure.in')) and _is_build(Path('m4/os.m4'))
