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

    # ---- 1b. animated cards: capture frames DURING the CSS animation ----
    # scale.html and close.html animate themselves, so screenshotting over
    # time yields real motion frames (DOM animation — no canvas involved).
    for name, seconds in (("scale", 13.0), ("close", 8.0)):
        pg2 = browser.new_page(viewport={"width": 1920, "height": 1080},
                               device_scale_factor=1)
        d = OUT / name
        if d.exists():
            for old in d.iterdir():
                old.unlink()          # stale frames would break f%04d numbering
        d.mkdir(exist_ok=True)
        pg2.goto((REPO / f"{name}.html").resolve().as_uri(), wait_until="load")
        pg2.wait_for_timeout(1000)     # first line fully entered before frame 0
        stamps = []
        t_end = time.time() + seconds
        while time.time() < t_end:
            i = len(stamps)
            # JPEG with a .jpg name: ffmpeg's png decoder rejects jpeg bytes
            pg2.screenshot(path=str(d / f"f{i:04d}.jpg"), type="jpeg",
                           quality=92)
            stamps.append(time.time())
            pg2.wait_for_timeout(110)
        span = stamps[-1] - stamps[0]
        (OUT / f"{name}.txt").write_text(f"{len(stamps)} {span}\n")
        ok.append(f"{name}: {len(stamps)} frames over {span:.2f}s "
                  f"(scene {seconds:.0f}s)")
        pg2.close()

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
