"""C/C++ lexer position and literal handling tests."""
from qnx_portcheck.lexer import comment_stripped, lex

def test_comments_strings_and_positions() -> None:
    source = 'int x; // erased\nconst char *a="x\\\"y"; /*multi\ncomment*/ char q = \'"\';\n'
    code, strings, comments = lex(source)
    assert len(code) == len(source)
    assert code.count("\n") == source.count("\n")
    assert strings[0] == (2, 15, 'x\\\"y')
    assert "erased" not in comments and "comment" not in comments
    assert "multi" not in comment_stripped(source)
    assert all(code[index] == "\n" for index, char in enumerate(source) if char == "\n")
    assert code.splitlines()[1][14] == '"'
    assert code.splitlines()[1][15:18] == '   '

def test_raw_strings_and_line_continuation_comment() -> None:
    source = '// hidden \\\ncontinued comment\nconst char *raw = u8R"x(quote " and\n/proc/test)x";\n'
    code, strings, comments = lex(source)
    assert len(code) == len(source)
    assert "continued comment" not in comments
    assert strings == [(3, 22, 'quote " and\n/proc/test')]
    assert "hidden" not in code and "/proc/test" not in code

def test_multiline_comment_preserves_line_and_column() -> None:
    source = 'int value; /* first\n second */\nint ready = epoll_wait(fd, 0, 1, 0);\n'
    code, strings, _ = lex(source)
    assert strings == []
    assert code.splitlines()[2].index("epoll_wait") == source.splitlines()[2].index("epoll_wait")
