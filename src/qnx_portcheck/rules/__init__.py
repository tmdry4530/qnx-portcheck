"""Rule registry."""
from .base import Hit, Rule, SourceContext
from .io_multiplex import RULES as _io
from .linux_apis import RULES as _apis
from .procfs import RULES as _procfs
from .buildfiles import RULES as _build

ALL_RULES: tuple[Rule, ...] = tuple(_io + _apis + _procfs + _build)
RULES_BY_ID = {rule.id: rule for rule in ALL_RULES}

__all__ = ["Hit", "Rule", "SourceContext", "ALL_RULES", "RULES_BY_ID"]
