"""Text, JSON, and SARIF report serializers."""
from __future__ import annotations

import json
from pathlib import Path
from . import __version__
from .rules import ALL_RULES
from .scanner import Finding

def _sorted(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda item: (item.file, item.line, item.col, item.rule_id))

def to_json(findings: list[Finding], root: Path) -> dict:
    """Serialize findings using the stable public JSON schema."""
    return {"tool": "qnx-portcheck", "version": __version__, "root": str(root), "findings": [
        {"rule_id": item.rule_id, "severity": item.severity, "file": item.file,
         "line": item.line, "col": item.col, "message": item.message,
         "suggestion": item.suggestion, "doc_url": item.doc_url,
         "confidence": item.confidence} for item in _sorted(findings)]}

def to_text(findings: list[Finding], files_scanned: int) -> str:
    """Render a human-readable report and summary."""
    rows = []
    for item in _sorted(findings):
        row = f"{item.file}:{item.line}:{item.col}: {item.severity} [{item.rule_id}] {item.message}\n    suggestion: {item.suggestion}"
        if item.doc_url:
            row += f"\n    doc: {item.doc_url}"
        rows.append(row)
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    notes = sum(item.severity == "note" for item in findings)
    rows.append(f"{len(findings)} finding(s): {errors} error, {warnings} warning, {notes} note in {files_scanned} file(s) scanned")
    return "\n".join(rows) + "\n"

def to_sarif(findings: list[Finding], root: Path) -> dict:
    """Render SARIF 2.1.0 with a stable complete rule registry."""
    rules = []
    for rule in ALL_RULES:
        item = {"id": rule.id, "name": rule.id,
                "shortDescription": {"text": rule.title},
                "fullDescription": {"text": rule.suggestion},
                "defaultConfiguration": {"level": rule.severity},
                "properties": {"confidence": rule.confidence}}
        if rule.doc_url:
            item["helpUri"] = rule.doc_url
        rules.append(item)
    indices = {rule["id"]: index for index, rule in enumerate(rules)}
    results = [{"ruleId": item.rule_id, "ruleIndex": indices[item.rule_id],
        "level": item.severity, "message": {"text": item.message + " — " + item.suggestion},
        "locations": [{"physicalLocation": {"artifactLocation": {"uri": item.file, "uriBaseId": "SRCROOT"},
                         "region": {"startLine": item.line, "startColumn": item.col}}}],
        "properties": {"confidence": item.confidence, "doc_url": item.doc_url}}
        for item in _sorted(findings)]
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": "qnx-portcheck", "version": __version__,
                "informationUri": "https://github.com/tmdry4530/qnx-portcheck", "rules": rules}},
                "originalUriBaseIds": {"SRCROOT": root.as_uri() + "/"}, "results": results}]}
