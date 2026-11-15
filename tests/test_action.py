from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
ROOT = Path(__file__).resolve().parents[1]


def test_action_contract_and_workflow():
    action = yaml.safe_load((ROOT / "action/action.yml").read_text())
    workflow = yaml.safe_load((ROOT / "examples/workflows/qnx-portcheck.yml").read_text())

    assert action["runs"]["using"] == "composite"
    expected = {
        "path": ".",
        "sarif-file": "qnx-portcheck.sarif",
        "python-version": "3.12",
        "upload": "true",
        "category": "qnx-portcheck",
    }
    for name, default in expected.items():
        assert action["inputs"][name]["default"] == default

    steps = action["runs"]["steps"]
    run_steps = [step for step in steps if "run" in step]
    assert run_steps
    for step in run_steps:
        assert step.get("shell") == "bash"
        assert "${{ inputs." not in step["run"]
    scan = next(step for step in run_steps if "qnx-portcheck scan" in step["run"])
    assert "--format sarif" in scan["run"]
    upload = next(step for step in steps if step.get("uses", "").startswith("github/codeql-action/upload-sarif@"))
    assert upload["uses"] == "github/codeql-action/upload-sarif@v4"

    triggers = workflow.get("on", workflow.get(True, {}))
    assert "pull_request" in triggers
    assert workflow["permissions"]["security-events"] == "write"
