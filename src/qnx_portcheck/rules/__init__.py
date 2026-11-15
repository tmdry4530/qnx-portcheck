"""Rule registry."""
from dataclasses import replace
from .base import Hit, Rule, SourceContext
from .io_multiplex import RULES as _io
from .linux_apis import RULES as _apis
from .procfs import RULES as _procfs
from .buildfiles import RULES as _build
from .platform import RULES as _platform
from .build_platform import RULES as _build_platform

_LINUX_GUARDED = {"LNX-EPOLL", "LNX-EVENTFD", "LNX-TIMERFD", "LNX-SIGNALFD",
                  "LNX-INOTIFY", "LNX-PRCTL", "LNX-SYSINFO", "LNX-SENDFILE",
                  "LNX-SPLICE", "LNX-SYSCALL", "LNX-ACCEPT4", "LNX-PIPE2",
                  "LNX-LINUX-HEADER", "LNX-PROCFS"}
# Optional facilities that projects enable through a build probe (HAVE_SYS_EPOLL_H, EVENT__HAVE_EPOLL,
# USBI_TIMERFD_AVAILABLE, ASIO_HAS_TIMERFD, ...): code inside such a branch is compiled only when the probe
# succeeds, so the finding belongs to the build configuration, not to the guarded call.
_FEATURE_TOKENS = {"LNX-EPOLL": "EPOLL", "LNX-EVENTFD": "EVENTFD", "LNX-TIMERFD": "TIMERFD",
                   "LNX-SIGNALFD": "SIGNALFD", "LNX-INOTIFY": "INOTIFY"}
ALL_RULES: tuple[Rule, ...] = tuple(
    replace(rule, skip_in_linux_guard=rule.id in _LINUX_GUARDED,
            feature_token=_FEATURE_TOKENS.get(rule.id))
    for rule in _io + _apis + _procfs + _build + _platform + _build_platform
)
RULES_BY_ID = {rule.id: rule for rule in ALL_RULES}

__all__ = ["Hit", "Rule", "SourceContext", "ALL_RULES", "RULES_BY_ID"]
