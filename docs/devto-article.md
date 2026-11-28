# dev.to article — готовий текст для публікації (крок 55)

**Стан:** чернетка готова **28.11.2026**, опублікувати **4–5.12** (за планом).
**Де публікувати:** dev.to → *Write a post* → вставити цей Markdown →4 теги → *Publish*.
**Чому 4–5.12:** код уже заморожено (крок45), публікація напередодні вікна
голосування; за R6 це **3-й кандидат на зріз** — якщо часу немає, ріжеться
після GIF і5-го запиту.

**Теги (dev.to обмежує4):** `graphdatabase` · `cypher` · `neo4j` · `ai`
(запасні: `mcp`, `llm`, `agents`)

---

## Заголовок (варіанти)

1. **We stopped guessing what a product change breaks — and answered it with one Cypher question**
2. The blast radius of a product change, drawn as a path instead of a spreadsheet
3. What breaks if we stop selling this? A graph answer in 200 ms

## Текст статті

Every week an e-commerce team changes something: a SKU is retired, a brand is
renamed, a category merge lands. The blast radius of that one change is
scattered across product feeds, marketplace listings, price rules, campaigns,
landing pages and CRM segments — and today it lives in a spreadsheet plus
somebody's memory. Nobody finds the seventh consequence until it breaks.

**Why a spreadsheet cannot answer it.** The question is not "where did I write
this down", it is "what is connected to this". A vector store finds text that
*looks like* the question; it cannot say what breaks, because breakage lives in
relationships that have to be traversed: listing → product → category → feed
contract → rule. In SQL the same question is **ten tables** and a recursive
CTE. In a graph it is one variable-length pattern.

**What we built: Cascade.** A change-impact graph for e-commerce operations,
running on Relate as a **single file** — `store/catalog.rl`, 1.1 MB,
committed to the repository. No server, no signup, no directory to reconcile:
the whole interface is one command.

The store holds **1,667 nodes and 3,730 relationships** over a synthetic
600-product catalog (seed 42, generator included, deliberate defects planted so
they can be asserted rather than assumed). Seven questions are answered by
seven single statements — what breaks if we stop selling this product, why is
this listing rejected, what is invisible right now, what collides if we merge
two categories, which products get rejected next, is this promo still in force,
and what single fix clears the most risk.

**The answer arrives as a path, not a score.** The blast-radius query returns
**476 rows** in about **0.2 s** on a 2013 laptop without AVX2 — every row a
route from the change to its consequence, so the claim is reproducible instead
of asserted. `make report` opens with a one-line verdict you can paste into a
ticket: delisting `PU-1004` takes 2 listings offline, deadens 1 page, breaks 1
feed contract. Under it, the tables are live Cypher results.

**For agents, not just for people.** The store serves MCP over stdio with five
read-only tools — `read_cypher`, `get_schema`, `blast_radius`,
`rejection_causes`, `remediation` — so an agent answers "what breaks?" with
paths it can cite. The server refuses every write: it cannot delete anyone's
graph, including yours.

**What keeps it honest.** `make verify` runs **eleven gates** end to end from
a fresh clone in about **14 seconds**: committed store first, seven query
results, the MCP surface with CLI/MCP parity, baseline counts, an injection
test and a determinism check. `make golden` freezes demo, report and verify
output byte for byte, CI re-runs all of it on every push, and every number in
the README is checked against the store rather than typed in.

**What it is not.** No vector or hybrid retrieval, no live integrations, no
production data — the catalog is synthetic and disclosed as such, because
publishing a real one is not an option. Blast radius stops at four hops, and
absence of impact is not proof of safety.

**Try it in sixty seconds:**

```bash
curl -sSfL https://relatedb.ai/install.sh | bash   # one binary
git clone https://github.com/koztechie/cascade.git
cd cascade && make verify                          # == verify: OK ==
```

Then open `viewer.html` — the blast radius is already built, offline, no query
written — or give the repo to your agent through `.mcp.json`.

**Links**

- Code: https://github.com/koztechie/cascade
- Demo, 1:30 with voice and subtitles: https://youtu.be/EuO9WT4_lPc
- Submission page: https://devpost.com/software/cascade-kys6m8

---

*Built with AI assistance under the owner's direction — design, code, tests and
docs — while no AI runs at runtime: every answer is deterministic Cypher
against the store. The narration voice in the demo video is AI-generated
(Kokoro-82M, Apache-2.0), generated locally. Enter published as part of the
Relate by Neo4j Hackathon.*
