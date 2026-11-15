"""Validate the public JSON report schema and rule documentation links."""
import json
from pathlib import Path
from qnx_portcheck.cli import main
from qnx_portcheck.rules import ALL_RULES


def test_json_schema(tmp_path: Path) -> None:
    output_path = tmp_path / "out.json"
    fixtures = Path(__file__).parent / "fixtures"
    arguments = ["scan", str(fixtures), "--format", "json", "--out", str(output_path)]
    assert main(arguments) == 0
    data = json.loads(output_path.read_text())
    assert list(data) == ["tool", "version", "root", "findings"]
    for finding in data["findings"]:
        assert list(finding) == ["rule_id", "severity", "file", "line", "col", "message",
                                 "suggestion", "doc_url", "confidence"]
        assert finding["severity"] in {"error", "warning", "note"}
        assert finding["confidence"] in {"high", "medium", "manual-review"}
        assert finding["line"] >= 1 and finding["col"] >= 1
        assert not finding["file"].startswith("/") and "\\" not in finding["file"]
        url = finding["doc_url"]
        assert url is None or url.startswith("https://www.qnx.com/developers/docs/8.0/")
    assert all(rule.suggestion == "manual review" for rule in ALL_RULES if rule.doc_url is None)
    sources = (Path(__file__).parents[1] / "docs/rule-sources.md").read_text()
    assert all(rule.doc_url is None or rule.doc_url in sources for rule in ALL_RULES)
