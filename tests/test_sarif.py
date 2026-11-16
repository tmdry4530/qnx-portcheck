"""SARIF output structure checks."""
from pathlib import Path
from qnx_portcheck.scanner import scan
from qnx_portcheck.report import to_sarif

def test_sarif() -> None:
    result = scan(Path(__file__).parent / "fixtures")
    data = to_sarif(result.findings, result.root)
    assert data["version"] == "2.1.0"
    assert data["$schema"].endswith("sarif-2.1.0.json")
    run = data["runs"][0]
    driver = run["tool"]["driver"]
    rule_ids = [rule["id"] for rule in driver["rules"]]
    assert driver["name"] == "qnx-portcheck"
    assert driver["informationUri"] == "https://github.com/Heal-chamdom/qnx-portcheck"
    for item in run["results"]:
        assert item["ruleId"] in rule_ids
        assert rule_ids[item["ruleIndex"]] == item["ruleId"]
        assert item["level"] in {"error", "warning", "note"}
        assert item["locations"][0]["physicalLocation"]["region"]["startLine"] >= 1
