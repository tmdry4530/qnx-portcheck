from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

MKIFS = "https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.utilities/topic/m/mkifs.html"
BOOL = set("autolink big_pages bigendian compress dupignore followlink include keeplinked optional page_align raw script".split())
VALUE = set("autoso cd chain cksum compress dperms drop filter gid ifs_csa image keepsection linker module mount mtime pagesizes perms phys_align physical prefix ram search sha256 sha512 type uid virtual".split())

@dataclass
class Diagnostic:
    rule_id: str
    severity: str
    line: int
    col: int
    message: str
    doc_url: str


def _diag(out, rule, severity, line, col, message, section="Buildfiles"):
    anchors = {"Buildfiles": "mkifs__Buildfiles", "Attributes": "mkifs__Attributes"}
    out.append(Diagnostic(rule, severity, line, col, message, f"{MKIFS}#{anchors[section]}"))


def _logical_lines(text: str):
    """Buildfiles permit backslash-newline continuation outside inline files (mkifs Buildfiles)."""
    buf = ""
    start = 1
    for n, raw in enumerate(text.splitlines(), 1):
        if not buf:
            start = n
        # Continuations occur outside inline content; preserve a separator for tokenization.
        if raw.endswith("\\"):
            buf += raw[:-1] + " "
            continue
        yield start, buf + raw
        buf = ""
    if buf:
        yield start, buf


def _find_comment(line: str):
    quote = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            quote = not quote
        elif ch == "#" and not quote and (i == 0 or line[i-1].isspace()):
            return i
        elif ch == "#" and not quote:
            # Doc requires a separating space before a comment marker.
            return -i-1
    return None


def _bracket_end(s, start):
    depth = 0
    escaped = False
    for i in range(start, len(s)):
        c = s[i]
        if escaped:
            escaped = False
        elif c == "\\":
            escaped = True
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i
    return None


def lint_text(text: str, filename: str = "<string>") -> list[Diagnostic]:
    # QNX Buildfiles says # comments need a preceding space, attributes share one
    # bracket pair with no spaces around =, and inline contents are opaque except braces.
    # Attribute forms below follow the mkifs Attributes list and boolean/value descriptions.
    # Rule grounding (mkifs Buildfiles / Attributes): bracket attributes; use one
    # pair when combining them; keep whitespace away from `=`; boolean forms use
    # +/- and value forms use `=value`; the documented list is closed-world here.
    # QNX requires a space before # comments and disallows inline contents on either
    # brace line; contents are parsed only for the closing brace, which must be escaped.
    # Filenames may be quoted; paths should use forward slash directory separators.
    out: list[Diagnostic] = []
    inline = False
    inline_start = 0
    for line_no, raw in _logical_lines(text):
        stripped = raw.strip()
        if inline:
            # Inline bytes are opaque to mkifs except for escaped closing braces.
            if "}" in stripped and not stripped.startswith("\\}"):
                close = stripped.find("}")
                if stripped[:close].strip():
                    _diag(out, "BF-INLINE-CLOSE-CONTENT", "error", line_no, raw.find("}")+1, "Inline contents cannot share the closing-brace line.")
                # QNX says inline contents are only parsed for the closing brace;
                # a closing brace must be escaped inside inline contents.
                if not stripped[:close].rstrip().endswith("\\"):
                    inline = False
            continue
        if not stripped:
            continue
        ci = _find_comment(raw)
        if ci is not None and ci < 0:
            pos = -ci-1
            _diag(out, "BF-COMMENT-SPACE", "warning", line_no, pos+1, "Comment marker must be separated from the command by a space.")
            raw = raw[:pos]
        elif ci is not None:
            raw = raw[:ci]
        s = raw.strip()
        if not s:
            continue
        if s.startswith("}"):
            _diag(out, "BF-INLINE-STRAY-CLOSE", "error", line_no, raw.find("}")+1, "Closing brace outside an inline file.")
            continue
        pos = 0
        groups = []
        while pos < len(s) and s[pos] == "[":
            end = _bracket_end(s, pos)
            if end is None:
                _diag(out, "BF-ATTR-UNTERMINATED", "error", line_no, raw.find("[")+1, "Attribute bracket is not terminated.")
                pos = len(s)
                break
            groups.append((pos, end, s[pos+1:end]))
            pos = end + 1
            while pos < len(s) and s[pos].isspace(): pos += 1
        if len(groups) > 1:
            _diag(out, "BF-ATTR-MULTIPLE-GROUPS", "error", line_no, raw.find("[")+1, "Combine attributes in one bracket pair.")
        for _, _, body in groups:
            if re.search(r"\w+\s+=|=\s+\S", body):
                _diag(out, "BF-ATTR-EQUALS-SPACING", "error", line_no, raw.find("[")+1, "Do not put spaces around an attribute equals sign.", "Attributes")
            normalized = re.sub(r"\s*=\s*", "=", body)
            for tok in re.findall(r"(?<!\\)\S+", normalized):
                clean = tok.lstrip("?+-")
                name = clean.split("=", 1)[0]
                if name not in BOOL | VALUE:
                    _diag(out, "BF-ATTR-UNKNOWN", "warning", line_no, raw.find(tok)+1, f"Unknown mkifs attribute {name!r}.", "Attributes")
                elif "=" in clean and name in BOOL and name != "compress":
                    _diag(out, "BF-ATTR-KIND", "error", line_no, raw.find(tok)+1, f"Boolean attribute {name!r} cannot take a value.", "Attributes")
                elif tok.lstrip("?").startswith(("+", "-")) and name in VALUE and name != "compress":
                    _diag(out, "BF-ATTR-KIND", "error", line_no, raw.find(tok)+1, f"Value attribute {name!r} cannot use a boolean prefix.", "Attributes")
        rest = s[pos:].strip() if groups else s
        # A `}` before a comment closes only as a standalone line in inline parsing; opening on a spec line.
        if re.search(r"=\s*\{\s*$", rest):
            inline = True
            inline_start = line_no
            continue
        # Inline definitions may have a trailing comment after their opening brace.
        if re.search(r"=\s*\{\s+#", raw):
            inline = True
            inline_start = line_no
            continue
        if re.search(r"=\s*\{", rest):
            _diag(out, "BF-INLINE-OPEN-CONTENT", "error", line_no, raw.find("{")+2, "Inline contents cannot share the opening-brace line.")
            inline = True
            inline_start = line_no
            continue
        # An unquoted quote toggle signals malformed filename.
        quote = False; escaped = False
        for ch in rest:
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == '"': quote = not quote
        if quote:
            _diag(out, "BF-FILE-QUOTE", "error", line_no, raw.find('"')+1, "Unbalanced double quote in file specification.")
        # Backslashes in path are discouraged; permitted escapes are excluded.
        for m in re.finditer(r'\\(?![\\n$"\]])', rest):
            _diag(out, "BF-PATH-BACKSLASH", "note", line_no, raw.find("\\", pos)+1, "Use forward slashes for directory separators.")
            break
    if inline:
        _diag(out, "BF-INLINE-UNCLOSED", "error", inline_start, 1, "Inline file is not closed before end of file.")
    return out


def lint_file(path):
    p = Path(path)
    return lint_text(p.read_text(encoding="utf-8", errors="replace"), str(p))


def run(args):
    all_diags = []
    try:
        for filename in args.file:
            for d in lint_file(filename):
                all_diags.append((filename, d))
    except OSError as exc:
        print(f"{filename}: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps([{"file": f, **asdict(d)} for f, d in all_diags], indent=2))
    else:
        for f, d in all_diags:
            print(f"{f}:{d.line}:{d.col}: {d.severity}: {d.rule_id}: {d.message} ({d.doc_url})")
    return 1 if any(d.severity == "error" for _, d in all_diags) else 0


def register(subparsers):
    parser = subparsers.add_parser("lint-buildfile", help="Check mkifs buildfile syntax")
    parser.add_argument("file", nargs="+")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.set_defaults(func=run)
    return parser


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lint-buildfile")
    subs = parser.add_subparsers(dest="command", required=True)
    register(subs)
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
