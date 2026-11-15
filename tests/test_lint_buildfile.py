import json
from pathlib import Path

from qnx_portcheck import lint_buildfile as lb

ROOT = Path(__file__).parent / "fixtures/buildfiles"


def test_eclipse_score_corpus_has_no_diagnostics():
    for path in sorted((ROOT / "eclipse-score").glob("*.build")):
        diagnostics = lb.lint_file(path)
        assert diagnostics == [], f"{path}: {diagnostics}"


def test_compress_boolean_and_value_forms():
    assert lb.lint_text("[-compress] a\n[+compress] a\n[compress=2] a\n") == []


def test_core_syntax_and_inline_opaque():
    text = '''[uid=5 gid=5] f
[?+bigendian] "file with spaces"
foo \\
  bar
script = {
# [uid = bad]
[+session]
\\}
still inline
}
'''
    assert lb.lint_text(text) == []


def test_bad_fixtures_expected_rules():
    expected = {
        "unterminated.build": "BF-ATTR-UNTERMINATED",
        "multiple.build": "BF-ATTR-MULTIPLE-GROUPS",
        "equals.build": "BF-ATTR-EQUALS-SPACING",
        "unknown.build": "BF-ATTR-UNKNOWN",
        "kind.build": "BF-ATTR-KIND",
        "comment.build": "BF-COMMENT-SPACE",
        "open-content.build": "BF-INLINE-OPEN-CONTENT",
        "close-content.build": "BF-INLINE-CLOSE-CONTENT",
        "unclosed.build": "BF-INLINE-UNCLOSED",
        "stray.build": "BF-INLINE-STRAY-CLOSE",
        "quote.build": "BF-FILE-QUOTE",
        "backslash.build": "BF-PATH-BACKSLASH",
    }
    for name, rule in expected.items():
        got = {d.rule_id for d in lb.lint_file(ROOT / "bad" / name)}
        assert got == {rule}, (name, got)


def test_cli_run_codes_and_json(capsys, tmp_path):
    good = tmp_path / "ok.build"
    good.write_text("foo\n")
    bad = tmp_path / "bad.build"
    bad.write_text("[uid = 5] foo\n")
    parser = __import__("argparse").ArgumentParser()
    subs = parser.add_subparsers()
    lb.register(subs)
    assert lb.run(parser.parse_args(["lint-buildfile", str(good)])) == 0
    assert lb.run(parser.parse_args(["lint-buildfile", str(bad)])) == 1
    capsys.readouterr()
    assert lb.run(parser.parse_args(["lint-buildfile", str(good), "--format", "json"])) == 0
    assert json.loads(capsys.readouterr().out) == []
    assert lb.run(parser.parse_args(["lint-buildfile", str(tmp_path / "missing")])) == 2


def test_rule_urls_documented():
    docs = (Path(__file__).parents[1] / "docs/buildfile-lint-rules.md").read_text()
    for path in list((ROOT / "bad").glob("*.build")):
        for d in lb.lint_file(path):
            assert d.doc_url in docs
            assert d.doc_url.startswith("https://www.qnx.com/developers/docs/8.0/")
