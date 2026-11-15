"""Rule fixture expectations and whole-tree false-positive checks."""
from pathlib import Path
import re

import pytest

from qnx_portcheck.rules import ALL_RULES
from qnx_portcheck.scanner import scan

BASE = Path(__file__).parent / "fixtures"


def _fixture(rule_id: str, state: str) -> Path:
    """Resolve a rule's positive or negative fixture."""
    slug = rule_id.lower().replace("lnx-", "").replace("-", "_")
    if rule_id.startswith("LNX-LINK"):
        filename = "CMakeLists.txt" if rule_id == "LNX-LINK-FLAGS" else "Makefile"
        return BASE / "build" / slug / state / filename
    return BASE / "c" / f"{slug}_{state}.c"


def _expected_lines(path: Path, rule_id: str) -> set[int]:
    """Read expected line numbers from same-line fixture markers."""
    return {
        number for number, line in enumerate(path.read_text().splitlines(), 1)
        if f"EXPECT: {rule_id}" in line
    }


@pytest.mark.parametrize("rule_id", [rule.id for rule in ALL_RULES])
def test_each_rule_has_exact_positive_lines_and_clean_negative(rule_id: str) -> None:
    positive = _fixture(rule_id, "pos")
    negative = _fixture(rule_id, "neg")
    assert positive.is_file() and negative.is_file()
    result = scan(positive)
    actual = {
        (finding.line, finding.rule_id) for finding in result.findings
        if finding.rule_id == rule_id
    }
    expected = {(line, rule_id) for line in _expected_lines(positive, rule_id)}
    assert actual == expected
    assert not [finding for finding in scan(negative).findings if finding.rule_id == rule_id]


def test_all_fixture_findings_are_marked() -> None:
    for finding in scan(BASE).findings:
        path = BASE / finding.file
        line = path.read_text().splitlines()[finding.line - 1]
        marker = rf"EXPECT:\s*{re.escape(finding.rule_id)}\b"
        assert re.search(marker, line), (finding, line)


def test_readme_lists_every_rule() -> None:
    readme = (BASE.parents[1] / "README.md").read_text()
    assert all(rule.id in readme for rule in ALL_RULES)
