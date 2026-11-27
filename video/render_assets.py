#!/usr/bin/env python3
"""Render every still/sequence asset the demo video needs.

Outputs to /tmp/opencode/vassets (disposable — this script regenerates it).
Sources of truth live in the repo: scene1.html, sql-contrast.html, viewer.html,
queries, and the MCP server.

Run:  python3 video/render_assets.py
"""
import json
import pathlib
import re
import subprocess
import time

from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path("/tmp/opencode/vassets")
(OUT / "viewer").mkdir(parents=True, exist_ok=True)

ok = []


def die(msg):
    raise SystemExit(f"FATAL: {msg}")


def first_dark_frame(video, fps=25, thresh=100):
    """Seconds until the page's dark background first paints.

    Playwright starts recording when the context is created, so the file
    opens on Chromium's blank white page; a scene has to be cut from the
    moment our own #0e1116 background appears.
    """
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf",
         f"fps={fps},scale=64:36,format=gray", "-f", "rawvideo", "-"],
        capture_output=True)
    block = 64 * 36
    data = r.stdout
    for i in range(len(data) // block):
        if sum(data[i * block:(i + 1) * block]) / block < thresh:
            return i / fps
    return 0.0


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080},
                            device_scale_factor=1)

    # ---- 1. question card: four reveal stages ----------------------------
    stages = [
        ('<span class="brand">Cascade</span>', "stage1"),
        ('<span class="brand">Cascade</span>'
         '<p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>', "stage2"),
        ('<span class="brand">Cascade</span>'
         '<p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>'
         '<hr class="rule">', "stage3"),
        ('<span class="brand">Cascade</span>'
         '<p class="q">We are discontinuing <b>PU-1004</b> — what breaks?</p>'
         '<hr class="rule">'
         '<p class="p">Know the blast radius before it breaks: one Cypher '
         'question returns a path through the graph — not a score.</p>', "stage4"),
    ]
    src = (REPO / "scene1.html").read_text(encoding="utf-8")
    head = src.split("<main>", 1)[0] + "<main>"
    for body, name in stages:
        html = head + body + "</main></html>"
        f = OUT / f"card-{name}.html"
        f.write_text(html, encoding="utf-8")
        page.goto(f.resolve().as_uri(), wait_until="load")
        page.wait_for_timeout(250)
        page.screenshot(path=str(OUT / f"card-{name}.png"))
    ok.append("card: 4 reveal stages")

    # ---- 1a. SQL contrast card (single still, zoom is added at encode) ----
    page.goto((REPO / "sql-contrast.html").resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(350)
    page.screenshot(path=str(OUT / "sql.png"))
    ok.append("sql: still")

    # ---- 1b. question card: the FULL card from frame 0 -------------------
    # Staged fragments produced two identical early frames and an empty first
    # frame, which breaks the step 27 rule that frame 0 carries the question.
    # A single still plus a slow zoom keeps frame 0 correct.
    page.goto((REPO / "scene1.html").resolve().as_uri(), wait_until="load")
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / "question.png"))
    ok.append("question: full still")

    # ---- 1b. animated cards: NATIVE PAGE RECORDING (25 fps) -------------
    # The old screenshot loop topped out at 1.76 fps here (358–614 ms per
    # full-page shot), so a 0.6 s CSS reveal was captured in a single frame
    # and the text snapped into place instead of gliding. Playwright's
    # recorder samples the compositor at 25 fps and measured identical to a
    # direct screenshot (edge sharpness 755 vs 751).
    for name, seconds in (("scale", 13.0), ("close", 8.0)):
        rec_dir = OUT / f"{name}.rec"
        if rec_dir.exists():
            for old in rec_dir.iterdir():
                old.unlink()
        rec_dir.mkdir(exist_ok=True)
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
                                  device_scale_factor=1,
                                  record_video_dir=str(rec_dir),
                                  record_video_size={"width": 1920,
                                                     "height": 1080})
        pg2 = ctx.new_page()
        pg2.goto((REPO / f"{name}.html").resolve().as_uri(), wait_until="load")
        # 1 s: the first line has fully entered — the same lead-in the old
        # screenshot loop waited for; +1 s so the cut never runs short.
        pg2.wait_for_timeout(1000 + int(seconds * 1000) + 1000)
        ctx.close()                     # flushes the .webm to disk
        rec = next(rec_dir.glob("*.webm"))
        # The recording opens on the browser's blank white page, so the
        # scene is cut from the first frame carrying our dark background.
        # +1.15 s = the 1 s lead-in the old screenshot loop waited for after
        # `load`, plus the ~0.1 s gap between first paint and that load event.
        # Measured against the shipped video: scale needs 1.09, close 1.05 —
        # 1.15 clears both, and the target state then holds for ~1.7 s.
        offset = first_dark_frame(rec) + 1.15
        dst = OUT / f"{name}.webm"
        if dst.exists():
            dst.unlink()
        rec.rename(dst)
        (OUT / f"{name}.txt").write_text(f"{offset:.3f}\n")
        ok.append(f"{name}: recorded 25 fps, scene cut at {offset:.2f}s "
                  f"(scene {seconds:.0f}s)")

    # ---- 2. viewer: capture sequence with a real click ------------------
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
                              device_scale_factor=1)
    vp = ctx.new_page()
    vp.goto((REPO / "viewer.html").resolve().as_uri(), wait_until="load")
    vp.wait_for_timeout(3000)
    stamps = []

    def snap():
        vp.screenshot(path=str(OUT / "viewer" / f"f{len(stamps):04d}.png"))
        stamps.append(time.time())

    t0 = time.time()
    while time.time() - t0 < 3.0:          # hold: full graph
        snap()
        vp.wait_for_timeout(200)
    geo = vp.evaluate("""() => {const c=document.querySelector('canvas');
        const r=c.getBoundingClientRect();
        const rp=cy.getElementById('4:rl-id:n127').renderedPosition();
        return {x:r.left+rp.x, y:r.top+rp.y};}""")
    vp.mouse.move(geo["x"], geo["y"])
    vp.wait_for_timeout(400)
    vp.mouse.click(geo["x"], geo["y"])     # the click
    vp.wait_for_timeout(600)
    st = vp.evaluate("""() => ({t:document.getElementById('p-title').textContent,
        p:getComputedStyle(document.getElementById('panel')).display})""")
    if st["p"] == "none" or not st["t"]:
        die(f"viewer click failed: {st}")
    t1 = time.time()
    while time.time() - t1 < 17.0:         # hold: focused state
        snap()
        vp.wait_for_timeout(200)
    span = stamps[-1] - stamps[0]
    (OUT / "viewer.txt").write_text(f"{len(stamps)} {span}\n")
    ok.append(f"viewer: {len(stamps)} frames, {span:.2f}s, click -> {st['t']}")

    # ---- 3. agent stages (SQL text from a live MCP call) ----------------
    Q = ("MATCH path = (l:Listing)-[:OFFERS]->(p:Product {sku:'PU-1004'})"
         "-[:IN_CATEGORY]->(c:Category)<-[:APPLIES_TO]-(m:Mapping)"
         "<-[:HAS_MAPPING]-(f:Feed) "
         "RETURN [n IN nodes(path) | labels(n)[0] + ': ' + "
         "coalesce(n.name, n.target_field, n.source_field, n.key, n.sku, "
         "n.url, n.id)] AS path, length(path) AS hops LIMIT 5")
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "cascade-demo", "version": "1.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "read_cypher", "arguments": {"query": Q}}},
    ]
    r = subprocess.run(
        ["./bin/relate", "serve", "--mcp", "stdio",
         "--database", "store/catalog.rl", "--read-only"],
        input="\n".join(json.dumps(m) for m in msgs) + "\n",
        capture_output=True, text=True, timeout=60, cwd=REPO)
    tools, call = [], None
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("id") == 2:
            tools = [t["name"] for t in o["result"]["tools"]]
        if o.get("id") == 3:
            call = o
    if not call or "error" in call:
        die(f"MCP exchange failed: {call}")
    payload = json.loads(call["result"]["content"][0]["text"])
    if not payload.get("row_count"):
        die(f"empty MCP answer: {payload}")
    (OUT / "mcp.json").write_text(
        json.dumps({"tools": tools, "query": Q, "payload": payload},
                   ensure_ascii=False, indent=1))
    ok.append(f"mcp: {len(tools)} tools, {payload['row_count']} rows x "
              f"{payload['rows'][0]['hops']} hops")

    # ---- 4. terminal outputs -------------------------------------------
    for cmd, name in (("make report", "report.out"),
                      ("make verify", "verify.out")):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=600, cwd=REPO)
        (OUT / name).write_text(r.stdout, encoding="utf-8", errors="replace")
        ok.append(f"{cmd}: exit={r.returncode}, {len(r.stdout.splitlines())} lines")

    browser.close()

print("\n".join(f"  OK  {x}" for x in ok))
print(f"assets in {OUT}")
