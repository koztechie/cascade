#!/usr/bin/env python3
"""Build the Cascade demo video v2: hard-cut structure built for impact.

Eight scenes, 90.000 s total, hard cuts (a punchier rhythm than crossfades),
an original score whose accents land on the reveals, and burned subtitles.

  1 question  10s   hook — first frame must be the question (step 27)
  2 scale     13s   600 / 1,667 / 3,730 -> 475 consequences -> 1 file
  3 viewer    17s   the path, revealed by a real click
  4 sql       11s   ten tables vs one pattern
  5 agent     17s   live MCP exchange, read-only claim
  6 verdict   9s    the one line from make report
  7 verify    5s    == verify: OK ==
  8 close     8s    pitch + repository + friction claims

Requires: python3 video/render_assets.py
Run:      python3 video/build_video.py
"""
import json
import math
import pathlib
import subprocess
import sys
import wave

import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
A = pathlib.Path("/tmp/opencode/vassets")
W = pathlib.Path("/tmp/opencode/vbuild")
OUT = REPO / "video" / "cascade-demo.mp4"
W.mkdir(parents=True, exist_ok=True)

FPS = 30
SCENES = [
    ("question", 10),
    ("scale",    13),
    ("viewer",   17),
    ("sql",      11),
    ("agent",    17),
    ("verdict",   9),
    ("verify",    5),
    ("close",     8),
]
assert sum(d for _, d in SCENES) == 90, sum(d for _, d in SCENES)


def sh(cmd: str) -> None:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1400:], file=sys.stderr)
        sys.exit(f"FAILED: {cmd[:170]}")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# terminal stage pages (unchanged styling from v1)
# --------------------------------------------------------------------------
TERM = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Cascade</title>
<style>
:root{--bg:#0e1116;--panel:#161b22;--text:#e6edf3;--muted:#8b949e;
      --accent:#58a6ff;--green:#3fb950}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--text)}
body{font:400 clamp(12px,1.08vw,19px)/1.5 ui-monospace,SFMono-Regular,
     Menlo,Consolas,monospace;-webkit-font-smoothing:antialiased}
main{min-height:100vh;display:flex;flex-direction:column;padding:5vh 4vw 17vh}
.term{flex:1;white-space:pre-wrap;word-break:break-word}
.ps{color:var(--green);font-weight:700}
.cmd{font-weight:600}
.dim{color:var(--muted)}
.ok{color:var(--green);font-weight:700}
.gate{color:var(--accent)}
.tools{color:var(--accent)}
.who{color:var(--text);font-weight:700;font-size:1.12em}
.call{color:var(--muted)}
.cy{color:#d2a8ff}
.res{color:var(--green);font-weight:700}
.out{margin:.25em 0 0;font:inherit;white-space:pre-wrap}
.verdict{color:var(--text);background:#1c2431;border-left:3px solid var(--accent);
         padding:.35em .6em;display:block;margin:.45em 0}
.title{position:absolute;left:0;right:0;bottom:0;background:var(--panel);
       border-top:2px solid var(--accent);padding:1.05em 4vw;
       font-size:.92em;line-height:1.45}
.title b{color:var(--accent)}
</style>
<main><div class="term">__BODY__</div></main>
__TITLE__</html>"""

T_AGENT = ('<div class="title"><b>Read-only and bounded — a deliberate choice.</b> '
           'For an analytics tool, refusing every write is a stronger guarantee than '
           'promising not to clobber: <b>it cannot delete anyone\'s graph, '
           'including yours.</b></div>')
T_VERDICT = ('<div class="title"><b>One line you can paste into a ticket.</b> '
             'make report writes the verdict first — every table under it is a '
             'live Cypher result.</div>')
T_VERIFY = ('<div class="title"><b>Eleven gates, then a green line.</b> '
            'make verify grades itself: queries, MCP surface, baselines, '
            'injection, determinism.</div>')


def stage_plans():
    """Return {name: ([(html, seconds)...], title)} for the staged scenes."""
    out = {}

    mcp = json.loads((A / "mcp.json").read_text())
    tools = "  ".join(mcp["tools"])
    rows = mcp["payload"]["rows"]
    q = (mcp["query"].replace(" RETURN ", "\n      RETURN ")
         .replace("MATCH path = ", "MATCH path =\n      ")
         .replace("-[:IN_CATEGORY]", "\n                -[:IN_CATEGORY]")
         .replace("<-[:APPLIES_TO]", "\n                <-[:APPLIES_TO]"))
    rowb = lambda r: "\n".join(f"    {p}" for p in r["path"])
    a1 = (f'<span class="ps">$</span> ./bin/relate serve --mcp stdio '
          f'--database store/catalog.rl --read-only\n'
          f'<span class="ok">connected</span> — 5 read-only tools:\n'
          f'<span class="tools">{tools}</span>')
    a2 = a1 + ('\n\n<span class="who">We are discontinuing PU-1004 — what '
               'breaks?</span>')
    a3 = a2 + f'\n\n<span class="call">→ read_cypher(</span>\n<span class="cy">{q}</span>\n<span class="call">)</span>'
    a4 = a3 + (f'\n\n<span class="res">→ {mcp["payload"]["row_count"]} rows · '
               f'{rows[0]["hops"]} hops</span>\n<pre class="out">{rowb(rows[0])}</pre>')
    a5 = a4 + f'\n\n<pre class="out">{rowb(rows[1])}</pre>'
    out["agent"] = ([(a1, 3), (a2, 3), (a3, 4), (a4, 4), (a5, 3)], T_AGENT)

    rep = (A / "report.out").read_text(errors="replace").splitlines()
    ri = next(i for i, l in enumerate(rep) if l.startswith("**Verdict:**"))
    cmd = '<span class="ps">$</span> <span class="cmd">make report</span>\n'
    gen = "".join(f'<span class="dim">{esc(l)}</span>\n' for l in rep[:6])
    ver = (f'<span class="verdict"><span class="ok">{esc(rep[ri])}</span></span>\n'
           + "".join(f'<span class="dim">{esc(l)}</span>\n'
                     for l in rep[ri + 1:ri + 4]))
    out["verdict"] = ([(cmd, 2), (cmd + gen, 3),
                       (cmd + gen + '<span class="dim">…</span>\n' + ver, 4)],
                      T_VERDICT)

    vo = (A / "verify.out").read_text(errors="replace").splitlines()
    gates = [i for i, l in enumerate(vo) if l.startswith("-- ")]
    vi = next(i for i, l in enumerate(vo) if "verify: OK" in l)
    vcmd = '<span class="ps">$</span> <span class="cmd">make verify</span>\n'
    head = "".join(f'<span class="gate">{esc(vo[i])}</span>\n' for i in gates[:6])
    rest = "".join(f'<span class="gate">{esc(vo[i])}</span>\n' for i in gates[6:])
    out["verify"] = ([(vcmd, 2),
                      (vcmd + head + '<span class="dim">…</span>\n' + rest +
                       f'<span class="ok">{esc(vo[vi])}</span>\n', 3)],
                     T_VERIFY)

    # question card: four reveal fragments of scene1.html
    src = (REPO / "scene1.html").read_text(encoding="utf-8")
    head, tail = src.split("<main>", 1)
    head += "<main>"
    tail = tail[tail.rindex("</main>"):]
    frags = ['<span class="brand">Cascade</span>',
             '<span class="brand">Cascade</span>\n  <p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>',
             '<span class="brand">Cascade</span>\n  <p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>\n  <hr class="rule">',
             '<span class="brand">Cascade</span>\n  <p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>\n  <hr class="rule">\n  <p class="p">Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.</p>']
    out["question"] = ([(head + f + tail, 2.5) for f in frags], None)
    return out


def render_stages(plan):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1920, "height": 1080},
                        device_scale_factor=1)
        result = {}
        for name, (parts, title) in plan.items():
            seq = []
            for i, (body, dur) in enumerate(parts, 1):
                html = TERM.replace("__BODY__", body).replace("__TITLE__",
                                                              title or "")
                f = W / f"{name}-{i}.html"
                f.write_text(html, encoding="utf-8")
                pg.goto(f.resolve().as_uri(), wait_until="load")
                pg.wait_for_timeout(220)
                png = W / f"{name}-{i}.png"
                pg.screenshot(path=str(png))
                seq.append((str(png), dur))
            result[name] = seq
        b.close()
    return result


def concat_stills(name, seq):
    """Hold each still for its duration; returns a clip path."""
    lines = []
    for png, dur in seq:
        lines += [f"file '{png}'", f"duration {dur}"]
    lines.append(f"file '{seq[-1][0]}'")
    listf = W / f"{name}-stills.txt"
    listf.write_text("\n".join(lines) + "\n")
    raw = W / f"{name}-raw.mp4"
    sh(f"ffmpeg -y -v error -f concat -safe 0 -i {listf} -vsync vfr "
       f"-vf fps={FPS},format=yuv420p -c:v libx264 -crf 16 -preset fast {raw}")
    return raw


def encode_sequence(name, frames_dir, span, total):
    """Encode a captured frame sequence to exactly `total` seconds.

    fps is derived from the SCENE length, not the measured capture span, so a
    capture that fell a fraction short still yields a full-length clip; the
    few percent of speed change is imperceptible.
    """
    n = len(list(frames_dir.glob("*.png"))) + len(list(frames_dir.glob("*.jpg")))
    fps = round(n / total, 3)
    raw = W / f"{name}-raw.mp4"
    pat = "f%04d.png" if list(frames_dir.glob("*.png")) else "f%04d.jpg"
    sh(f"ffmpeg -y -v error -framerate {fps} -i {frames_dir / pat} "
       f"-vf fps={FPS},format=yuv420p -c:v libx264 -crf 16 -preset fast "
       f"-t {total} {raw}")
    return raw


def encode_video(name, src, offset, total):
    """Cut `offset` seconds into a 25 fps page recording and conform it to
    exactly `total` seconds at 30 fps.

    Playwright records at 25 fps, so `fps=30` duplicates one frame in six.
    That regular pulldown is invisible next to the 17-frame holds it
    replaces (the old screenshot loop managed 1.76 fps).
    """
    raw = W / f"{name}-raw.mp4"
    sh(f'ffmpeg -y -v error -i "{src}" '
       f"-vf \"trim=start={offset}:duration={total},setpts=PTS-STARTPTS,"
       f"fps={FPS},format=yuv420p\" "
       f"-c:v libx264 -crf 16 -preset fast {raw}")
    return raw


def add_zoom(raw, total):
    """Slow continuous zoom so no frame is ever static.

    tpad clones the tail so a clip whose source is a fraction short still
    lands on its exact planned duration; -t then trims the ones that are long.
    """
    out = W / (raw.stem.replace("-raw", "") + ".mp4")
    # scale=4x first: zoompan rounds its crop box to whole pixels, so at 1x a
    # slow zoom jumped ~1 px every other frame (23% of scene 1's frames were
    # identical to their predecessor). At 4x the rounding is sub-pixel at
    # output: 0 frozen frames, motion irregularity CV 2.20 -> 0.28.
    sh(f"ffmpeg -y -v error -i {raw} -vf "
       f'"scale=7680:4320,zoompan=z=\'1+0.00032*on\':d=1:'
       f'x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':'
       f's=1920x1080:fps={FPS}",format=yuv420p,'
       f"tpad=stop_mode=clone:stop_duration=3 "
       f"-t {total} -c:v libx264 -crf 18 -preset fast {out}")
    return out


# --------------------------------------------------------------------------
# score: our own synthesised audio, so section 4 needs no third-party grant
# --------------------------------------------------------------------------
def build_score(path, seconds=90.0, sr=44100):
    n = int(seconds * sr)
    t = np.arange(n) / sr
    mix = np.zeros(n)

    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    mix += 0.30 * lfo * np.sin(2 * np.pi * 55.00 * t)
    mix += 0.17 * lfo * np.sin(2 * np.pi * 82.41 * t + 0.4)

    # pulse on a 100 BPM grid from the cold open onward
    ph = np.mod(t, 0.6)
    mix += 0.40 * np.exp(-ph / 0.085) * (t > 3.0) * np.sin(2 * np.pi * 52.0 * t)

    # pad across the middle
    pad = np.clip((t - 10.0) / 5.0, 0, 1) * np.clip((78.0 - t) / 7.0, 0, 1)
    for f in (220.00, 261.63, 329.63):
        mix += 0.085 * pad * np.sin(2 * np.pi * f * t + f)

    # accents: the scale reveal, the contrast, and the close
    for at, amp in ((10.0, 0.85), (40.0, 0.75), (82.0, 1.0)):
        hit = np.exp(-np.clip(t - at, 0, None) / 0.55) * (t >= at)
        mix += amp * hit * np.sin(2 * np.pi * 48.0 * t)
        mix += 0.30 * amp * hit * np.random.default_rng(int(at)).standard_normal(n)

    # riser into the closing card
    rise = np.clip((t - 74.0) / 7.0, 0, 1)
    mix += 0.15 * (rise ** 2) * np.sin(2 * np.pi * (220 + 1200 * rise) * t)
    mix += 0.09 * (rise ** 2) * np.random.default_rng(11).standard_normal(n)

    mix *= np.clip(t / 1.2, 0, 1)
    mix *= np.clip((seconds - t) / 1.2, 0, 1)
    mix = np.tanh(mix * 1.2)
    peak = np.max(np.abs(mix)) or 1.0
    mix *= 10 ** (-3.0 / 20.0) / peak

    delay = int(0.008 * sr)
    right = np.concatenate([np.zeros(delay), mix[:-delay]])
    stereo = np.stack([mix, 0.82 * right + 0.18 * mix], axis=1)
    with wave.open(str(path), "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())
    print(f"  score: {seconds:.0f}s  peak={20*math.log10(np.max(np.abs(mix))):.1f} dBFS  "
          f"rms={20*math.log10(np.sqrt(np.mean(mix**2))):.1f} dBFS")


SUBS = """1
00:00:00,400 --> 00:00:09,500
Every week an e-commerce team changes something — and nobody finds the seventh consequence until it breaks.

2
00:00:10,400 --> 00:00:22,500
The blast radius of a single change — counted, not estimated.

3
00:00:23,400 --> 00:00:39,500
Every answer arrives as a path — so the consequence is proven, not asserted.

4
00:00:40,400 --> 00:00:50,500
Ten tables and a recursive CTE — or one variable-length pattern.

5
00:00:51,400 --> 00:01:07,500
The agent gets connected context instead of a guess, and every sentence it says back can be checked against the edge that produced it.

6
00:01:08,000 --> 00:01:16,500
No Cypher required — the graph in business words.

7
00:01:17,400 --> 00:01:21,500
Every number comes from a run, not from typing.
"""


def main():
    print("1) stage pages …")
    plan = stage_plans()
    staged = render_stages(plan)

    print("2) encode scenes …")
    clips = []
    # CSS-animated scenes are page recordings: the screenshot loop only
    # managed 1.76 fps, which froze every 0.6 s reveal into a single frame.
    video_scenes = {}
    for name in ("scale", "close"):
        off = float((A / f"{name}.txt").read_text())
        video_scenes[name] = (A / f"{name}.webm", off)
    # viewer stays a frame sequence: a static graph plus one instant click,
    # so there is no smooth motion a faster capture would improve.
    n_v, span_v = (A / "viewer.txt").read_text().split()
    frame_scenes = {"viewer": (A / "viewer", float(span_v))}

    for name, total in SCENES:
        if name in video_scenes:
            src, off = video_scenes[name]
            raw = encode_video(name, src, off, total)
        elif name in frame_scenes:
            d, span = frame_scenes[name]
            raw = encode_sequence(name, d, span, total)
        elif name in ("sql", "question"):
            sh(f"ffmpeg -y -v error -loop 1 -i {A}/{name}.png -t {total} "
               f"-r {FPS} -vf format=yuv420p -c:v libx264 -crf 16 -preset fast "
               f"{W}/{name}-raw.mp4")
            raw = W / f"{name}-raw.mp4"
        else:
            raw = concat_stills(name, staged[name])
        clip = add_zoom(raw, total)
        clips.append(clip)
        print(f"  {name:9s} {total}s")

    print("3) score …")
    wav = W / "score.wav"
    build_score(wav)

    print("4) hard cuts + subtitles + score …")
    srt = W / "subs.srt"
    srt.write_text(SUBS, encoding="utf-8")
    # hard cuts: concat demuxer, then burn subtitles, then mux the score
    lst = W / "final-list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    # Encode beside the target, then rename: an interrupted build must not
    # be able to truncate the shipped deliverable (a server restart did
    # exactly that before this line existed).
    tmp = OUT.with_name(OUT.stem + ".part" + OUT.suffix)
    sh(f"ffmpeg -y -v error -f concat -safe 0 -i {lst} -i {wav} "
       f"-filter_complex \"[0:v]subtitles={srt}:force_style='FontName=DejaVu Sans,"
       f"FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,"
       f"Shadow=0,BorderStyle=1,MarginV=42,Alignment=2'[v]\" "
       f"-map \"[v]\" -map 1:a -c:v libx264 -crf 18 -preset medium "
       f"-pix_fmt yuv420p -c:a aac -b:a 192k -shortest "
       f"-movflags +faststart \"{tmp}\"")
    tmp.replace(OUT)
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
