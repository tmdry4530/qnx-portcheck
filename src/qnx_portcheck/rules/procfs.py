"""Linux procfs path rule."""
from __future__ import annotations

import re
from typing import Iterable

from .base import Hit, Rule, SourceContext

GENERAL = (
    "QNX 8.0 procnto implements /proc with a different layout (/proc/<pid>/ entries "
    "such as as, cmdline, ctl, exefile; /proc/self/ is the caller's address space). "
    "Linux files under /proc do not map 1:1; QNX docs say not to use /proc in "
    "production to control or monitor processes. Review this path manually."
)
SPECIAL = (
    "Linux /proc/self/exe does not exist on QNX 8.0; procnto exposes "
    "/proc/<pid>/exefile (the path of the executable file used to run the process). "
    "Note QNX docs say /proc is for debugging, not production monitoring."
)
DOCS_BASE = "https://www.qnx.com/developers/docs/8.0/"
DOC_URL = DOCS_BASE + "com.qnx.doc.neutrino.prog/topic/process_proc_filesystem.html"


def detect(context: SourceContext) -> Iterable[Hit]:
    """Find procfs paths at the beginning of string literals."""
    for line, col, value in context.strings:
        if not re.match(r"^/proc(?:/|$)", value):
            continue
        special = value.startswith("/proc/self/exe")
        yield Hit(
            line, col + 1, f'Linux /proc path "{value[:60]}"',
            confidence="high" if special else None,
            suggestion=SPECIAL if special else None,
        )


RULES = [Rule("LNX-PROCFS", "warning", "medium", "c", 'Linux /proc path "{literal}"',
              GENERAL, DOC_URL, detect)]
