"""Recognize preprocessor branches which QNX cannot compile."""
from __future__ import annotations
import re
from qnx_portcheck.lexer import line_starts

_cache: tuple[str, frozenset[int]] | None = None
_LINUX = {"__linux__", "__linux", "linux", "__gnu_linux__"}
_DIRECTIVE = re.compile(r'^\s*#\s*(if|ifdef|ifndef|elif|elifdef|elifndef|else|endif)\b(.*)')

def _linux_test(expr: str) -> bool:
    expr = re.sub(r'\s+', ' ', expr.strip())
    expr = re.sub(r'^\((.*)\)$', r'\1', expr)
    if '||' in expr:
        return False
    parts = re.split(r'&&', expr)
    return any(re.fullmatch(r'\s*(?:defined\s*(?:\(\s*|\s+))?(' + '|'.join(map(re.escape, _LINUX)) + r')(?:\s*\))?\s*', part) for part in parts)

def linux_only_lines(comments: str) -> frozenset[int]:
    global _cache
    line_starts(comments)
    if _cache is not None and _cache[0] is comments:
        return _cache[1]
    frames: list[dict[str, bool]] = []
    result: set[int] = set()
    for number, line in enumerate(comments.splitlines(), 1):
        match = _DIRECTIVE.match(line)
        if not match and any(frame["branch"] for frame in frames):
            result.add(number)
        if not match:
            continue
        op, arg = match.group(1), match.group(2).strip()
        if op in {"if", "ifdef", "ifndef"}:
            macro = arg.split()[0] if arg else ""
            then_linux = ((op == "ifdef" and macro in _LINUX)
                          or (op == "if" and _linux_test(arg)))
            else_linux = ((op == "ifndef" and macro in _LINUX)
                          or (op == "if" and bool(re.fullmatch(
                              r"!\s*defined\s*(?:\(\s*)?(?:__linux__|__linux|linux|__gnu_linux__)(?:\s*\))?", arg))))
            frames.append({"branch": then_linux, "else_linux": else_linux})
        elif op in {"elif", "elifdef", "elifndef"} and frames:
            macro = arg.split()[0] if arg else ""
            frames[-1]["branch"] = ((op == "elifdef" and macro in _LINUX)
                                     or (op == "elif" and _linux_test(arg)))
        elif op == "else" and frames:
            frames[-1]["branch"] = frames[-1]["else_linux"]
        elif op == "endif" and frames:
            frames.pop()
    answer = frozenset(result)
    _cache = (comments, answer)
    return answer


_feature_cache: dict[str, tuple[str, frozenset[int]]] = {}


def _positive_feature_test(op: str, arg: str, token: str) -> bool:
    """True when the branch is taken only if a macro naming the facility is defined/true."""
    if op in {"ifdef", "elifdef"}:
        name = arg.split()[0] if arg else ""
        return token in name.upper()
    if op in {"if", "elif"}:
        if "||" in arg:
            return False
        for conjunct in arg.split("&&"):
            text = conjunct.strip().strip("()").strip()
            if text.startswith("!"):
                continue
            if re.search(r"\b\w*" + token + r"\w*\b", text, re.I) and not re.search(r"\b\w*" + token + r"\w*\s*(==|<=|<)\s*0\b", text, re.I):
                return True
    return False


def feature_guarded_lines(comments: str, token: str) -> frozenset[int]:
    """Lines inside a branch that is compiled only when a build-probe macro naming ``token`` is set.

    Examples for token EPOLL: ``#ifdef HAVE_SYS_EPOLL_H``, ``#if defined(EVENT__HAVE_EPOLL)``,
    ``#if ASIO_HAS_EPOLL && !defined(X)``. Negated tests and ``||`` conditions are not guards.
    """
    cached = _feature_cache.get(token)
    if cached is not None and cached[0] is comments:
        return cached[1]
    frames: list[bool] = []
    result: set[int] = set()
    for number, line in enumerate(comments.splitlines(), 1):
        match = _DIRECTIVE.match(line)
        if not match:
            if any(frames):
                result.add(number)
            continue
        op, arg = match.group(1), match.group(2).strip()
        if op in {"if", "ifdef", "ifndef"}:
            frames.append(_positive_feature_test(op, arg, token))
        elif op in {"elif", "elifdef", "elifndef"} and frames:
            frames[-1] = _positive_feature_test(op, arg, token)
        elif op == "else" and frames:
            frames[-1] = False
        elif op == "endif" and frames:
            frames.pop()
    answer = frozenset(result)
    _feature_cache[token] = (comments, answer)
    return answer
