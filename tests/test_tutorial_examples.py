from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_daemon_variants_compile(tmp_path):
    compiler = shutil.which("cc") or shutil.which("gcc")
    if not compiler:
        pytest.skip("no C compiler available")
    for source in ("filewatchd.c", "filewatchd_poll.c"):
        subprocess.run(
            [compiler, "-Wall", "-Wextra", "-Werror", "-std=c11", "-D_GNU_SOURCE",
             str(ROOT / "examples/linux-daemon/src" / source), "-o", str(tmp_path / source.removesuffix(".c"))],
            check=True,
        )


def test_tutorial_sources_and_verification_notes():
    tutorial = (ROOT / "docs/tutorial-port-linux-daemon-to-qnx8.md").read_text()
    sources = (ROOT / "docs/tutorial-sources.md").read_text()
    import re
    urls = re.findall(r"https://www\.qnx\.com\S+", tutorial)
    for url in urls:
        assert url.rstrip("),.;`") in sources
    assert "NOT VERIFIED" in tutorial
    assert (ROOT / "examples/linux-daemon/qnx/filewatchd.build").is_file()
