from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demo"))
import build_assets


def test_scenes_and_budgets():
    scenes = build_assets.load_scenes()
    ids = [scene["id"] for scene in scenes]
    assert ids == [f"{i:02d}" for i in range(7)]
    assert len(set(ids)) == len(ids)
    assert sum(scene["duration"] for scene in scenes) < 180
    for scene in scenes:
        words = build_assets.word_count(" ".join(scene["narration"]))
        assert words / 150 * 60 <= scene["duration"] - 1
    assert build_assets.word_count(" ".join(sentence for s in scenes for sentence in s["narration"])) / 150 * 60 < 180


def test_scene_output_paths_are_temporary():
    for scene in build_assets.load_scenes():
        for command in scene["commands"]:
            words = command.split()
            for index, word in enumerate(words[:-1]):
                if word == "--out":
                    assert words[index + 1].startswith("/tmp/qnx-demo/")


def test_script_is_current_and_honest():
    script = (ROOT / "demo/script.md").read_text(encoding="utf-8")
    assert build_assets.HONESTY in script
    assert "[EVAL_NUMBERS]" in script
    assert script == build_assets.render_script()


def test_srt_round_trip_and_offsets(tmp_path):
    for scene in build_assets.load_scenes():
        cues = build_assets.make_cues(scene["narration"], scene["duration"])
        text = build_assets.format_srt(cues)
        parsed = build_assets.parse_srt(text)
        assert len(parsed) == len(cues)
        assert all(a < b <= scene["duration"] for a, b, _ in parsed)
        assert all(parsed[i][1] <= parsed[i + 1][0] for i in range(len(parsed) - 1))
        assert all(build_assets._timestamp(a) in text and build_assets._timestamp(b) in text for a, b, _ in parsed)
    build_assets.build_subs(tmp_path)
    total = sum(scene["duration"] for scene in build_assets.load_scenes())
    assert build_assets.parse_srt((tmp_path / "demo.srt").read_text())[-1][1] <= total


def test_shell_syntax_and_shellcheck():
    scripts = list((ROOT / "demo").glob("*.sh")) + list((ROOT / "demo/scenes").glob("*.sh"))
    for script in scripts:
        subprocess.run(["bash", "-n", str(script)], check=True)
    shellcheck = shutil.which("shellcheck") or ("/home/box/.local/bin/shellcheck" if Path("/home/box/.local/bin/shellcheck").exists() else None)
    if not shellcheck:
        pytest.skip("shellcheck not installed")
    subprocess.run([shellcheck, *map(str, scripts)], check=True)


def test_demo_visual_layout_and_exit_statuses():
    record = (ROOT / "demo/record.sh").read_text(encoding="utf-8")
    assert "$REPO_ROOT/$OUT" not in record
    assert "scale=1280:590:force_original_aspect_ratio=decrease" in record
    assert "pad=1280:720:(ow-iw)/2:4:color=0x1e1e1e" in record
    assert "FontName=DejaVu Sans,FontSize=16,Outline=1,MarginV=8" in record
    assert "y=220" in record and "y=560" not in record
    scene = (ROOT / "demo/scenes/04-lint.sh").read_text(encoding="utf-8")
    assert "export DEMO_SHOW_EXIT=1" in scene
    assert "'no diagnostics'" in scene

    command = "source demo/scenes/lib.sh; DEMO_SHOW_EXIT=1 DEMO_PAUSE=0 DEMO_TYPE_DELAY=0 show_cmd 'true' 'no diagnostics'; DEMO_SHOW_EXIT=1 DEMO_PAUSE=0 DEMO_TYPE_DELAY=0 show_cmd 'false' || true"
    output = subprocess.run(["bash", "-c", command], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    assert "(exit 0: no diagnostics)" in output
    assert "(exit 1)" in output


def test_gitignore_has_output():
    assert "demo/out/" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_scaffold_wrapper(tmp_path):
    project = tmp_path / "sample"
    project.mkdir()
    (project / "CMakeLists.txt").write_text("project(sample)\n")
    command = "source demo/scenes/lib.sh; qnx-portcheck scaffold '" + str(project) + "' --dry-run"
    subprocess.run(["bash", "-c", command], cwd=ROOT, env={**__import__('os').environ, "DEMO_TYPE_DELAY": "0", "DEMO_PAUSE": "0"}, check=True, stdout=subprocess.PIPE, text=True)
