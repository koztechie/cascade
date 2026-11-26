#!/usr/bin/env python3
"""Build the Cascade demo video: motion, crossfades, original score, subtitles.

Pipeline
--------
  1. terminal stage pages  -> PNG   (finer staging = more on-screen events)
  2. scenes                -> mp4   (staged reveals + slow zoom via zoompan)
  3. score                 -> wav   (synthesised here: our own work, CC-free)
  4. xfade chain + burned subtitles + score -> video/cascade-demo.mp4 (90 s)

Requires: video/render_assets.py has been run (assets in /tmp/opencode/vassets).
Run:       python3 video/build_video.py
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
D_XFADE = 0.5
# source durations chosen so the xfade chain lands on exactly 90.000 s
SCENES = {
    "card":   16,
    "viewer": 21,
    "agent":  20,
    "report": 18,
    "verify": 17,
}
ORDER = ["card", "viewer", "agent", "report", "verify"]


def sh(cmd: str) -> None:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:], file=sys.stderr)
        sys.exit(f"FAILED: {cmd[:160]}")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# 1. terminal stage pages
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
T_REPORT = ('<div class="title"><b>One line you can paste into a ticket.</b> '
            'make report writes the verdict first — every table under it is a '
            'live Cypher result.</div>')
T_VERIFY = ('<div class="title"><b>Eleven gates, then a green line.</b> '
            'make verify grades itself: queries, MCP surface, baselines, '
            'injection, determinism.</div>')


def build_stages():
    """Return {scene: [(png, seconds), ...]} for the three terminal scenes."""
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
    out["agent"] = ([(a1, 3), (a2, 4), (a3, 5), (a4, 4), (a5, 4)], T_AGENT)

    rep = (A / "report.out").read_text(errors="replace").splitlines()
    ri = next(i for i, l in enumerate(rep) if l.startswith("**Verdict:**"))
    cmd = '<span class="ps">$</span> <span class="cmd">make report</span>\n'
    gen = "".join(f'<span class="dim">{esc(l)}</span>\n' for l in rep[:6])
    ver = (f'<span class="verdict"><span class="ok">{esc(rep[ri])}</span></span>\n'
           + "".join(f'<span class="dim">{esc(l)}</span>\n'
                     for l in rep[ri + 1:ri + 4]))
    r1 = cmd
    r2 = cmd + gen
    r3 = cmd + gen + '<span class="dim">…</span>\n' + ver
    r4 = r3 + "".join(f'<span class="dim">{esc(l)}</span>\n'
                      for l in rep[ri + 4:ri + 9])
    out["report"] = ([(r1, 3), (r2, 4), (r3, 5), (r4, 6)], T_REPORT)

    ver_out = (A / "verify.out").read_text(errors="replace").splitlines()
    gates = [i for i, l in enumerate(ver_out) if l.startswith("-- ")]
    vi = next(i for i, l in enumerate(ver_out) if "verify: OK" in l)
    vcmd = '<span class="ps">$</span> <span class="cmd">make verify</span>\n'
    head = "".join(f'<span class="gate">{esc(ver_out[i])}</span>\n'
                   for i in gates[:4])
    mid = "".join(f'<span class="gate">{esc(ver_out[i])}</span>\n'
                  for i in gates[4:8])
    tail = "".join(f'<span class="gate">{esc(ver_out[i])}</span>\n'
                   for i in gates[8:])
    okl = f'<span class="ok">{esc(ver_out[vi])}</span>\n'
    v1 = vcmd
    v2 = vcmd + head
    v3 = vcmd + head + mid
    v4 = vcmd + head + mid + tail
    v5 = v4 + okl
    out["verify"] = ([(v1, 3), (v2, 4), (v3, 4), (v4, 3), (v5, 3)], T_VERIFY)
    return out


def render_stage_pages(stages):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1920, "height": 1080},
                        device_scale_factor=1)
        plan = {}
        for name, (parts, title) in stages.items():
            seq = []
            for i, (body, _dur) in enumerate(parts, 1):
                html = TERM.replace("__BODY__", body).replace("__TITLE__", title)
                f = W / f"{name}-{i}.html"
                f.write_text(html, encoding="utf-8")
                pg.goto(f.resolve().as_uri(), wait_until="load")
                pg.wait_for_timeout(200)
                png = W / f"{name}-{i}.png"
                pg.screenshot(path=str(png))
                seq.append((str(png), _dur))
            plan[name] = seq
        b.close()
    return plan


def encode_scene(name, seq, total):
    """Concatenate staged stills with their hold times, then add a slow zoom."""
    listf = W / f"{name}-stills.txt"
    lines = []
    for png, dur in seq:
        lines.append(f"file '{png}'")
        lines.append(f"duration {dur}")
    lines.append(f"file '{seq[-1][0]}'")   # ffmpeg concat quirk: repeat last
    listf.write_text("\n".join(lines) + "\n")

    # how many frames this scene must produce
    n = int(round(total * FPS))
    raw = W / f"{name}-raw.mp4"
    sh(f"ffmpeg -y -v error -f concat -safe 0 -i {listf} -vsync vfr "
       f"-vf fps={FPS},format=yuv420p -c:v libx264 -crf 16 -preset fast {raw}")

    # continuous slow zoom (motion on every frame) + drift-free centring
    zoom = W / f"{name}.mp4"
    sh(f"ffmpeg -y -v error -i {raw} -vf "
       f'"zoompan=z=\'1+0.00030*on\':d=1:'
       f'x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':'
       f's=1920x1080:fps={FPS}",format=yuv420p '
       f"-t {total} -c:v libx264 -crf 18 -preset fast {zoom}")
    return zoom


# --------------------------------------------------------------------------
# 3. original score — synthesised, so it is our own work (Section 4 safe)
# --------------------------------------------------------------------------
def build_score(path: pathlib.Path, seconds: float = 90.0, sr: int = 44100):
    n = int(seconds * sr)
    t = np.arange(n) / sr
    mix = np.zeros(n, dtype=np.float64)

    # sustained drone: A1 + fifth
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    mix += 0.30 * lfo * np.sin(2 * np.pi * 55.00 * t)
    mix += 0.18 * lfo * np.sin(2 * np.pi * 82.41 * t + 0.4)

    # soft sub pulse on a 100 BPM grid, entering after the cold open
    period = 0.6
    phase = np.mod(t, period)
    env = np.exp(-phase / 0.085) * (t > 5.0)
    mix += 0.42 * env * np.sin(2 * np.pi * 52.0 * t)

    # pad chord from the first scene change, fading out before the ending
    pad_env = np.clip((t - 14.0) / 6.0, 0, 1) * np.clip((74.0 - t) / 8.0, 0, 1)
    for f in (220.00, 261.63, 329.63):
        mix += 0.085 * pad_env * np.sin(2 * np.pi * f * t + f)

    # riser into the final beat
    rise = np.clip((t - 70.0) / 16.0, 0, 1)
    sweep = np.sin(2 * np.pi * (200.0 + 1300.0 * rise) * t)
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n)
    mix += 0.16 * (rise ** 2) * sweep + 0.10 * (rise ** 2) * noise

    # impact on the closing frame
    hit = np.exp(-np.clip(t - 86.5, 0, None) / 0.45) * (t >= 86.5)
    mix += 0.55 * hit * np.sin(2 * np.pi * 48.0 * t)
    mix += 0.22 * hit * noise

    # fades and soft limit
    mix *= np.clip(t / 1.5, 0, 1)
    mix *= np.clip((seconds - t) / 1.5, 0, 1)
    mix = np.tanh(mix * 1.15)
    peak = np.max(np.abs(mix)) or 1.0
    mix *= 10 ** (-3.0 / 20.0) / peak          # -3 dBFS peak

    # gentle stereo width: tiny delay + detune on the right channel
    delay = int(0.008 * sr)
    right = np.concatenate([np.zeros(delay), mix[:-delay]])
    right = 0.82 * right + 0.18 * mix
    stereo = np.stack([mix, right], axis=1)
    data = (stereo * 32767).astype(np.int16)

    with wave.open(str(path), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    rms = float(np.sqrt(np.mean(mix ** 2)))
    print(f"  score: {seconds:.0f}s  peak={20*math.log10(np.max(np.abs(mix))):.1f} dBFS  "
          f"rms={20*math.log10(rms):.1f} dBFS")


# --------------------------------------------------------------------------
def main():
    print("1) stage pages …")
    plan = render_stage_pages(build_stages())

    print("2) encode scenes (staged reveals + slow zoom) …")
    clips = {}
    # card + viewer come from pre-rendered assets, terminals from `plan`
    card_seq = [(str(A / f"card-stage{i}.png"), d)
                for i, d in enumerate([3, 4, 4, 5], 1)]
    n_v, span_v = (A / "viewer.txt").read_text().split()
    fps_v = round(int(n_v) / float(span_v), 3)
    clips["card"] = encode_scene("card", card_seq, SCENES["card"])
    # viewer: image2 sequence at its real capture pace, then zoom.
    # NOTE: the concat demuxer collapses an image list without `duration`
    # entries into a single frame — use the pattern demuxer instead.
    sh(f"ffmpeg -y -v error -framerate {fps_v} -i {A}/viewer/f%04d.png "
       f"-vf fps={FPS},format=yuv420p -c:v libx264 -crf 16 -preset fast "
       f"{W}/viewer-raw.mp4")
    sh(f"ffmpeg -y -v error -i {W}/viewer-raw.mp4 -vf "
       f'"zoompan=z=\'1+0.00030*on\':d=1:'
       f'x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':'
       f's=1920x1080:fps={FPS}",format=yuv420p -t {SCENES["viewer"]} '
       f"-c:v libx264 -crf 18 -preset fast {W}/viewer.mp4")
    clips["viewer"] = W / "viewer.mp4"
    for name in ("agent", "report", "verify"):
        clips[name] = encode_scene(name, plan[name], SCENES[name])
        print(f"  {name}: {SCENES[name]}s")

    print("3) score …")
    wav = W / "score.wav"
    build_score(wav)

    print("4) assemble: xfade + subtitles + score …")
    srt = W / "subs.srt"
    srt.write_text(SUBS, encoding="utf-8")
    fc = [
        f"[0:v][1:v]xfade=transition=fade:duration={D_XFADE}:offset={16-D_XFADE}[a]",
        f"[a][2:v]xfade=transition=fade:duration={D_XFADE}:offset={16+21-2*D_XFADE}[b]",
        f"[b][3:v]xfade=transition=fade:duration={D_XFADE}:offset={16+21+20-3*D_XFADE}[c]",
        f"[c][4:v]xfade=transition=fade:duration={D_XFADE}:offset={16+21+20+18-4*D_XFADE}[v]",
        f"[v]subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=17,"
        f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,"
        f"Shadow=0,BorderStyle=1,MarginV=42,Alignment=2'[vo]",
    ]
    ins = " ".join(f"-i {clips[c]}" for c in ORDER)
    sh(f"ffmpeg -y -v error {ins} -i {wav} -filter_complex \"{' ; '.join(fc)}\" "
       f"-map \"[vo]\" -map 5:a -c:v libx264 -crf 18 -preset medium "
       f"-pix_fmt yuv420p -c:a aac -b:a 192k -shortest "
       f"-movflags +faststart \"{OUT}\"")
    print(f"  -> {OUT}")


SUBS = """1
00:00:00,000 --> 00:00:07,500
The blast radius of that one change is scattered across product feeds, marketplace listings, price rules, campaigns, landing pages and CRM segments

2
00:00:07,500 --> 00:00:15,000
— today it lives in spreadsheets and tribal knowledge, and nobody finds the seventh consequence until it breaks.

3
00:00:15,800 --> 00:00:25,500
Every answer arrives as a path — so the consequence is proven, not asserted.

4
00:00:25,500 --> 00:00:35,500
The path is the proof — not a confidence score, not a summary: a route through the graph you can open in the viewer and run again yourself.

5
00:00:36,300 --> 00:00:55,000
The agent gets connected context instead of a guess, and every sentence it says back can be checked against the edge that produced it.

6
00:00:55,800 --> 00:01:04,000
No Cypher required — the graph in business words: a product sits in a category; it has listings on marketplaces;

7
00:01:04,000 --> 00:01:12,500
each feed demands certain fields (a missing gtin gets a listing rejected); rules and campaigns point at categories; pages link products and categories.

8
00:01:13,000 --> 00:01:21,500
Every number in this README comes from a run, not from typing.

9
00:01:21,500 --> 00:01:29,500
The demo, report and verify outputs are compared byte-for-byte against committed fixtures, so a refactor cannot quietly change an answer.
"""

if __name__ == "__main__":
    main()
