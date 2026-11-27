from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "demo"))
import build_assets
import check_final


@pytest.mark.parametrize("text,expected", [
    ("Recall: [EVAL_NUMBERS] here", ["[EVAL_NUMBERS]"]),
    ("[ABC] and [X9_Y]", ["[ABC]", "[X9_Y]"]),
    ("TODO: fill", ["TODO"]),
    ("value TBD.", ["TBD"]),
    ("FIXME later", ["FIXME"]),
    ("see XXX", ["XXX"]),
    ("PLACEHOLDER: scan CLI not merged yet", ["PLACEHOLDER"]),
    ("a placeholder stays", ["placeholder"]),
])
def test_find_placeholders_positive(text, expected):
    assert check_final.find_placeholders(text) == expected


@pytest.mark.parametrize("text", [
    "com.qnx.<baselineId>.target.screen.notify_fd",
    "todo list and tbd and fixme in lower case",
    "warning [LNX-EPOLL] Linux epoll header",
    "[AB] is too short; [lower] is lower case",
    "XXXL TODOS FIXMES",
    "Fresh split: source-site recall 0.123 (12/97)",
])
def test_find_placeholders_negative(text):
    assert check_final.find_placeholders(text) == []


def test_scene_sources_pass_on_repo():
    assert check_final.check_scene_sources() == []


def test_scene_sources_reject_other_tokens(tmp_path):
    scenes = build_assets.load_scenes()
    scenes[1]["narration"].append("[EVAL_NUMBERS] misplaced.")
    scenes[6]["card_text"] += "\nTODO"
    path = tmp_path / "scenes.json"
    path.write_text(json.dumps(scenes))
    errors = check_final.check_scene_sources(path)
    assert len(errors) == 2
    assert "scene 01 narration" in errors[0] and "scene 06 card_text" in errors[1]


def _cast(path, *outputs):
    lines = [json.dumps({"version": 2, "width": 100, "height": 28})]
    lines += [json.dumps([0.1 * i, "o", text]) for i, text in enumerate(outputs, 1)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture
def render(tmp_path):
    if build_assets.load_eval(ROOT / "eval/RESULTS.md")[0] is None:
        pytest.skip("eval/RESULTS.md does not hold a valid run")
    build_assets.build_subs(tmp_path / "subs", eval_path=str(ROOT / "eval/RESULTS.md"))
    (tmp_path / "cards").mkdir()
    (tmp_path / "casts").mkdir()
    (tmp_path / "cards/00.txt").write_text("A host-side Linux to QNX 8.0 portability checker")
    (tmp_path / "cards/00-title.txt").write_text("qnx-portcheck")
    _cast(tmp_path / "casts/01.cast", "$ q", "nx-portcheck scan\r\n", "\x1b[33mwarning\x1b[0m <baselineId>\r\n")
    return tmp_path


def test_clean_render_passes(render):
    assert check_final.check_render(render)[0] == []
    assert check_final.check_srt_matches_burn_in(render) == []
    assert check_final.main(["--render", str(render)]) == 0


def test_mutated_cue_timing_fails(render):
    srt = render / "subs/demo.srt"
    text = srt.read_text()
    stamps = re.findall(r"\d{2}:\d{2}:\d{2},\d{3}", text)
    target = stamps[5]
    bumped = target[:-3] + f"{(int(target[-3:]) + 1) % 1000:03d}"
    srt.write_text(text.replace(target, bumped, 1))
    errors = check_final.check_srt_matches_burn_in(render)
    assert errors and "cue 3" in errors[0]


def test_dropped_cue_fails(render):
    srt = render / "subs/demo.srt"
    blocks = srt.read_text().strip().split("\n\n")
    srt.write_text("\n\n".join(blocks[:-1]) + "\n")
    assert check_final.check_srt_matches_burn_in(render)


def test_card_placeholder_fails(render):
    (render / "cards/05-headline.txt").write_text("[EVAL_NUMBERS]\n")
    errors, _ = check_final.check_render(render)
    assert any("05-headline.txt" in e and "[EVAL_NUMBERS]" in e for e in errors)


def test_cast_output_placeholder_fails(render):
    _cast(render / "casts/02.cast", "result: TO", "DO\r\n")
    errors, _ = check_final.check_render(render)
    assert any("02.cast" in e and "TODO" in e for e in errors)


def test_eval_status_placeholder_fails(render):
    (render / "subs/eval_status.txt").write_text("placeholder: missing\n")
    errors, _ = check_final.check_render(render)
    assert any("eval_status.txt" in e for e in errors)


def test_final_dir_srt_must_match(render, tmp_path_factory):
    final = tmp_path_factory.mktemp("final")
    srt = (render / "subs/demo.srt").read_bytes()
    (final / "qnx-portcheck-demo.srt").write_bytes(srt)
    assert check_final.check_final_dir(render, final) == []
    (final / "qnx-portcheck-demo.srt").write_bytes(srt.replace(b"\n", b"\r\n"))
    assert check_final.check_final_dir(render, final)


def test_lib_runs_real_cli():
    assert 'python3 -m qnx_portcheck.cli "$@"' in (ROOT / "demo/scenes/lib.sh").read_text(encoding="utf-8")


def test_closing_card_states_host_only_caveats():
    scene = next(s for s in build_assets.load_scenes() if s["id"] == "06")
    for phrase in ("no QNX SDP used", "no QNX target run", "triage aid, not an oracle"):
        assert phrase in scene["card_text"]


def _fake_ffprobe(monkeypatch, frames, rate="30/1", returncode=0):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        stdout = json.dumps({"streams": [{"r_frame_rate": rate, "nb_read_frames": str(frames)}]})
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="boom")

    monkeypatch.setattr(check_final.subprocess, "run", run)
    return calls


def test_video_frames_exact_passes(monkeypatch):
    calls = _fake_ffprobe(monkeypatch, 4830)
    assert check_final.check_video_frames("x.mp4", 161) == []
    assert "-count_frames" in calls[0] and "stream=nb_read_frames,r_frame_rate" in calls[0]


@pytest.mark.parametrize("frames,rate,needle", [
    (4825, "30/1", "4825 video frames"),
    (4830, "30000/1001", "r_frame_rate 30000/1001"),
])
def test_video_frames_mismatch_fails(monkeypatch, frames, rate, needle):
    _fake_ffprobe(monkeypatch, frames, rate)
    errors = check_final.check_video_frames("x.mp4", 161)
    assert len(errors) == 1 and needle in errors[0]


def test_video_frames_ffprobe_failure(monkeypatch):
    _fake_ffprobe(monkeypatch, 0, returncode=1)
    assert "ffprobe failed" in check_final.check_video_frames("x.mp4", 161)[0]

    def missing(command, **kwargs):
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(check_final.subprocess, "run", missing)
    assert "ffprobe not found" in check_final.check_video_frames("x.mp4", 161)[0]


def test_final_video_checks_frames_and_last_cue(tmp_path, monkeypatch):
    render, final = tmp_path / "render", tmp_path / "final"
    (render / "subs").mkdir(parents=True)
    final.mkdir()
    (render / "subs/scenes.tsv").write_text("id\tslug\tkind\tduration\trequires\n00\ttitle\tcard\t8\t\n01\tscan\tterminal\t2.5\t\n")
    assert check_final.check_final_video(render, final) == []
    (final / "qnx-portcheck-demo.mp4").write_bytes(b"")
    srt = final / "qnx-portcheck-demo.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:10,500\nlast\n")
    _fake_ffprobe(monkeypatch, 315)
    assert check_final.check_final_video(render, final) == []
    srt.write_text("1\n00:00:00,000 --> 00:00:10,501\nlast\n")
    errors = check_final.check_final_video(render, final)
    assert len(errors) == 1 and "last cue ends at 10.501s" in errors[0]
