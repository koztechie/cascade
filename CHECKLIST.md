# Submission checklist — Relate by Neo4j Hackathon

Deadline: **11 December 2026, 18:00 PST** (≈ 04:00, 12 December, Kyiv).
Internal target: **submit by 9 December**, leave a 2-day buffer.

## Hard requirements (an entry missing any of these may not be scored)

- [ ] Public GitHub repository, stays public through judging (16 Dec) and winner announcement (17 Dec)
- [ ] GitHub topic `relate` added (required); also `relate-neo4j-hackathon` (recommended)
- [ ] Persistent Relate store committed (`store/catalog.rl`, single-file mode)
- [ ] Working code with Relate actually running (not prompts only)
- [ ] README answers: how are you using Relate, and why? Includes mode, why this mode, what the graph models, setup and run, where the data lives
- [ ] Demo video, 1–2 minutes
- [ ] Devpost submission created and confirmed before 9 Dec

## Quality gates (what separates winners from strong entries)

- [ ] One-sentence pitch identical in: repo title, GitHub description, first README line, first video frame
- [ ] Cover image / GIF on the Devpost page (viewer with highlighted blast radius)
- [ ] Fresh-clone dry run: `git clone` → `make verify` → green, with no manual fixes
- [x] `make verify` passes on a clean state (including the MCP surface: handshake, read query, write refusal)
- [x] Numbers measured and in README: node/relationship counts, query timings (PROFILE)
- [x] Limitations section present (`docs/limitations.md`)
- [x] Static viewer built (`viewer.html`, offline, no install)
- [ ] Video: first frame = the question; SQL-contrast frame; MCP agent scene; burned-in subtitles
- [ ] dev.to article published (also feeds the community vote)
- [ ] Interacted on the Devpost discussions page / Neo4j community

## Final check on 8–9 December

- [ ] Repo is public, topic tags present
- [ ] README renders correctly on GitHub
- [ ] Video uploaded and playable on Devpost
- [ ] All checkboxes above ticked or consciously cut (cut order: ontology → vector retrieval → counterfactual extras)
- [ ] Submit, then re-open the submission page and confirm it shows as submitted
