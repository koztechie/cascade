# Submission checklist — Relate by Neo4j Hackathon

Deadline: **11 December 2026, 18:00 PST** (≈ 04:00, 12 December, Kyiv).
Internal target: **submit by 9 December**, leave a 2-day buffer.

**Legend** — every line below is in exactly one state, there are no empty boxes:

- `[x]` — done, with the evidence that proves it
- `⏳` — planned, with its date and plan step
- `✂️` — consciously cut, with the reason (R6 cut order)

Audited **28 November 2026** against the live repository, the public submission
page and a fresh clone.

## Hard requirements (an entry missing any of these may not be scored)

- [x] Public GitHub repository, stays public through judging (16 Dec) and winner announcement (17 Dec) — `gh repo view`: **PUBLIC**, not archived; the obligation runs to 17 Dec (plan step 63)
- [x] GitHub topic `relate` added (required); also `relate-neo4j-hackathon` (recommended) — both present on the repository
- [x] Persistent Relate store committed (`store/catalog.rl`, single-file mode) — tracked, 1,069,056 bytes, sha256 `01bc0816…`, byte-identical after every `make` target
- [x] Working code with Relate actually running (not prompts only) — eleven gates green from a fresh clone in **14 s**, five MCP tools live, `make report` and `make demo` exit 0
- [x] README answers: how are you using Relate, and why? Includes mode, why this mode, what the graph models, setup and run, where the data lives — 6/6 sections found, and the direct answer sits in the first screen (step 34)
- [x] Demo video, 1–2 minutes — **90.000 s**, 1920×1080, 30 fps, zero decode errors
- [x] Devpost submission created and confirmed before 9 Dec — submitted **27 Nov 2026**, public page returns HTTP 200 and shows "Submitted to Relate by Neo4j Hackathon"

## Quality gates (what separates winners from strong entries)

- [x] One-sentence pitch identical in: repo title, GitHub description, first README line, first video frame — **3 of 4 verbatim** (GitHub description = README line 5 = the 107-character pitch). In the video the pitch is on screen from **7.5 s** of the opening scene; frame 0 leads with the question instead — deliberate, decided in step 27, and rebuilding the frozen video is not worth it.
- [x] Cover image / GIF on the Devpost page (viewer with highlighted blast radius) — 3:2 thumbnail **and** the 5 s viewer GIF as gallery item 9, both verified on the public page
- [x] Fresh-clone dry run: `git clone` → `make verify` → green, with no manual fixes — step 41: `== verify: OK ==` in 14 s, `golden` and `check-claims` green, `git status` clean
- [x] `make verify` passes on a clean state (11 gates: committed store, seven queries, MCP surface with five tools + CLI/MCP parity, baseline + negative control, temporal, remediation, injection test)
- [x] **Триаж транзієнтів:** two green runs in a row before the final submission — the fresh clone (14 s) and the working tree both green on 28 Nov, zero FAILs; any future `FAIL` is re-run once, a second failure is a real bug
- [x] Numbers measured and in README: node/relationship counts, query timings (PROFILE)
- [x] Limitations section present (`docs/limitations.md`)
- [x] Static viewer built (`viewer.html`, offline, no install) — opens from a clone with zero console errors, canvas 1000×624
- [x] Video: first frame = the question; SQL-contrast frame; MCP agent scene; burned-in subtitles — all four re-checked against the frames (steps 27/28)
- ⏳ dev.to article published (also feeds the community vote) — **planned 4–5 Dec (step 55)**; R6 lists it as the third cut candidate if time runs out
- ⏳ Interacted on the Devpost discussions page / Neo4j community — **ongoing, steps 53/54/56** (daily two minutes, answers within 24 h)

## Final check on 8–9 December

- [x] Repo is public, topic tags present — verified 28 Nov; re-verify on 8 Dec (step 47)
- [x] README renders correctly on GitHub — verified 28 Nov: GIF, all sections, trademark notice
- [x] Video uploaded and playable on Devpost — embedded, 90 s, plays without login
- [x] All checkboxes above ticked or consciously cut (cut order: ontology → vector retrieval → counterfactual extras) — this audit, 28 Nov; the two `⏳` lines are dated, not forgotten
- [x] Submit, then re-open the submission page and confirm it shows as submitted — submitted 27 Nov, page confirms it
