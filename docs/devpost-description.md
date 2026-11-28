# Devpost "About the project" — готовий текст для чернетки #1314206

**Призначення:** текст між маркерами `ПОЧАТОК` / `КІНЕЦЬ` вставляється в поле
`* About the project` (сторінка 2 форми, markdown). Поле зараз **порожнє**.

- Редагування: `https://devpost.com/submit-to/32024-relate-by-neo4j-hackathon/manage/submissions/1314206-cascade/project-overview`
- У агента **немає сесії Devpost** (перевірено: redirect на `secure.devpost.com/users/login`),
  тому вставка — **твоя рука**, за кроком 47/50.
- Дублює **нічого зайвого**: шаблон конкурсу (див. нижче) + обов'язкові заяви §4.

## Шаблон, звірений дослівно зі сторінки конкурсу (23.11.2026)

```
# Project name
One-line pitch.
## Use case
What problem it solves and which relationships matter.
## How it uses Relate
- Mode: in memory | directory | single file
- Why this mode:
- What the graph models:
## Setup and run
Prerequisites, install steps, and the commands to reach a first result.
## Where the data lives
Path to the persistent store in this repo.
```

Чекліст подачі (та сама сторінка): **«Project description: the use case, and
what connects to what»** — тому «what connects to what» винесено в окрему
секцію, а не сховано в текст.

**Обов'язкові заяви (§4 Submission Requirements):** *«A statement of which
Product capabilities, third-party tools, and AI tools the project uses»* —
остання секція тексту нижче. §3 дослівно: *«meaningful use of Relate, for
example through the CLI, embedded use, WebAssembly, MCP, Bolt or HTTP, hybrid
retrieval, or a connection to Neo4j or Aura»* — перелік «for example», тобто
**не вичерпний**; ми вживаємо лише ті поверхні, якими справді користуємось,
а Bolt/HTTP/Rust подаємо **позитивно** (що вмикається, коли каталог
виросте), а не як перелік того, «чого не зробили». Гібридний retrieval /
вектор **не згадуємо** (поза обсягом; це не пропуск, якщо мовчати).

---

## ПОЧАТОК ТЕКСТУ ДЛЯ ВСТАВЛЕННЯ

# Cascade

**Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.**

## Use case

E-commerce teams change something every week: a SKU is discontinued, a brand is
renamed, prices rise 10%, two categories merge. The blast radius of that one
change is scattered across product feeds, marketplace listings, price rules,
campaigns, landing pages and CRM segments — today it lives in spreadsheets and
tribal knowledge, and nobody finds the seventh consequence until it breaks.

**Who this is for:** the e-commerce **operations manager** who owns the weekly
change spreadsheet — SKU retired, price moved, categories merged — together
with marketplace/feed managers and the AI agents that assist them. You learn
the seventh consequence **before it breaks**, not on Friday in production.

**The challenge asks for connected data that helps "agents, apps, or people" —
Cascade answers with all three from one graph:** the **agent** over MCP (five
read-only tools), the **app** as `viewer.html` and a one-line `make report`,
and the **person** above — an operations manager who never has to write
Cypher.

Cascade answers seven of those questions, one Cypher statement each: what
breaks if we stop selling this product · why is this listing rejected · what
is invisible or unlinked right now · what collides if we merge two categories
(a dry run) · which products will be rejected next · is this promo still in
force · what single fix clears the most risk. **No Cypher required to read the
answer** — the queries are how it is checked, not what you are asked to write.

**Why it is useful, in numbers:** one discontinued product expands into **476
consequences** across a **600-product** catalog, and both the path and the
**one-line verdict** come back from a single statement — the weekly change
conversation that lives in a spreadsheet becomes something a person reads in
a minute and an agent can re-run on demand.

**Why a graph:** a vector store finds text that *looks like* the question; it
cannot say **what breaks**, because breakage lives in relationships that have
to be traversed (listing → product → category → feed contract → rule), not in
similarity. So every answer arrives as a **path** — the consequence is proven,
not asserted. In SQL the same question is **ten tables** and a recursive CTE;
here it is one pattern.

## What connects to what

- `Product` → `Listing` → `Marketplace` — where it is actually sold
- `Product` → `Category` → `Rule`, `Campaign`, `Segment` — the commercial machinery pointed at it
- `Category` → `Mapping` → `Feed` — the field contract each feed enforces (e.g. a required `gtin`)
- `Page` → `Product` / `Category` — what the site shows and links

Change one node and the graph shows what else moves — with the reason beside
each edge. Where a link *should* exist and doesn't, the missing edge **is** the
answer (orphan pages, invisible stock).

## How it uses Relate

- **Mode:** single file (`store/catalog.rl`) — **1.1 MB**, committed to the repository.
- **Why this mode:** one file *is* the whole database. No server, no signup, no
  directory to reconcile; the whole interface is
  `relate query --database store/catalog.rl`. Copy it, commit it, mail it, move
  it to another machine and the graph travels with it.
- **What the graph models:**

  | Node | Meaning |
  | --- | --- |
  | `Product`, `Brand`, `Category`, `Supplier` | the catalog itself |
  | `Listing`, `Marketplace`, `Feed`, `Mapping` | where it is published, and the field contract each feed enforces |
  | `Rule`, `Campaign`, `Segment` | the commercial machinery pointed at the catalog |
  | `Page` | landing / category / product pages on the site |

  Relationships: `IN_CATEGORY`, `HAS_BRAND`, `SUPPLIED_BY` · `OFFERS`,
  `PUBLISHED_ON` · `HAS_MAPPING`, `APPLIES_TO` · `TARGETS`, `FILTERS_BY` ·
  `FEATURES`, `COVERS`, `LINKS_TO`. **1,667 nodes and 3,730 relationships.**

## What is verified before you trust a number

Every figure above comes from a run, and each one can be traced to the thing
that produced it:

| Claim | Where it is checked |
| --- | --- |
| What the seven queries return | `make verify` gates `01`–`04`, `06`, `08`, `09` assert the expected rows |
| Eleven gates exist | `scripts/check_claims.sh` counts the gate markers inside `scripts/verify.sh` |
| Five read-only MCP tools, by name | `check-claims` asks the live server for `tools/list` |
| 1,667 nodes · 3,730 relationships · 600 products · 553 clean | `verify` gate `07` (self-grading), reconciled against the README |
| Outputs cannot drift during a refactor | `make golden` compares demo, report and verify output byte for byte |
| One-line verdict | the `**Verdict:**` line `make report` writes |

The store is **synthetic** (seed 42, generator in this repository, deliberate
defects planted and asserted), because a public dataset of e-commerce
*operations* does not exist and publishing a real catalog is not an option.
That is a deliberate choice, not a shortcut: **no production, regulated or
employer data appears anywhere** — not in the store, not in the screenshots,
not in this submission — and nothing here derives from anyone else's
proprietary information.
**No AI runs inside the product:** every runtime answer is deterministic Cypher
against the store.

## Setup and run

Prerequisites: Python 3.8+ and the `relate` binary — no server, no signup.

```bash
# 1. install relate — one binary
curl -sSfL https://relatedb.ai/install.sh | bash

# 2. clone, build the store, verify everything
git clone https://github.com/koztechie/cascade.git
cd cascade
make verify
```

Expected output ends with `== verify: OK ==` (about **12–17 s** on a 2013 floor
machine). On hardware the prebuilt CLI does not support, `bin/relate` drives
the same engine through the pinned Python client — same commands, same store.

**From zero to an answer, in this order:**

1. Open [`viewer.html`](https://github.com/koztechie/cascade/blob/main/viewer.html) —
   the demo blast radius, already built: offline, no server, **no query
   written**. That is the first insight.
2. `make verify` — eleven gates, ending `== verify: OK ==`.
3. `make report` — a paste-into-a-ticket markdown report that opens with a
   **one-line verdict**, again with no Cypher.
4. Give it to your agent — `.mcp.json` (any MCP client), `opencode.json`
   (OpenCode) or `.agents/skills/cascade/SKILL.md` wire in
   **five read-only tools**: `read_cypher`, `get_schema`, `blast_radius`,
   `rejection_causes`, `remediation`. Then ask: *"We are discontinuing
   PU-1004 — what breaks?"* A recorded transcript — including the agent
   correcting its own first query — is in `docs/agent-session.md`.

## Where the data lives

- `store/catalog.rl` — the persistent Relate store, **committed** to this repository.
- `data/load.cypher` — the generated load script (`scripts/generate_data.py`, seed 42).
- `data/demo_params.json` — the demo SKU and category pair used by the queries.

The dataset is synthetic: realistic structure, deliberate defects, no real
business data — and the generator ships in the repository, so every row can be
audited.

## Product capabilities, third-party tools and AI tools

**Product capabilities (Relate):** the project makes meaningful use of Relate
through the **CLI** (`relate query`), **embedded use** (the `relate_db` Python
client behind `bin/relate`, which also serves the MCP surface) and **MCP** (five
read-only tools over stdio), against a single-file `.rl` store, with Cypher as
the query language. Bolt, HTTP and the Rust and Python libraries are the
surfaces that switch on when a catalog outgrows a single process — see
**Beyond one file** in the README: the same queries run on Neo4j / Neo4j Aura,
and a subgraph can be pulled into Relay for local work and pushed back.

**Third-party tools:** `cytoscape.js` (MIT, vendored in `vendor/`) for the
viewer; Relate and the `relate_db` client (Apache-2.0).

**AI tools:** AI-assisted development — design, code, tests and docs produced
with AI under the project owner's direction. **No AI runs at runtime**: every
answer is deterministic Cypher against the store, and where a model and the
graph disagree, the graph wins. The **narration voice in the demo video is
AI-generated** — Kokoro-82M (Apache-2.0), run locally on CPU: no cloud service,
no account. The video's music bed is synthesised by this repository's own build
script, so **no third-party audio is used anywhere in the video**.

**Originality, start date and prompts:** written for this contest — work began
**21 November 2026**, inside the contest window. **No pre-existing code was
reused**: neither third-party application code nor earlier code of our own —
everything here was built for this submission. The **prompts** are part of the
record as well: [`docs/agent-session.md`](https://github.com/koztechie/cascade/blob/main/docs/agent-session.md)
holds the exact prompts, the Cypher the agent wrote and the results, including
the moment the agent corrected its own first query.

## КІНЕЦЬ ТЕКСТУ ДЛЯ ВСТАВЛЕННЯ

---

## Чек-лист перед вставкою

- [ ] Усі **5 заголовків шаблону** на місці і в правильному порядку
      (`Use case` → `How it uses Relate` з `- Mode:` / `- Why this mode:` /
      `- What the graph models:` → `Setup and run` → `Where the data lives`).
- [ ] Є окрема секція **`What connects to what`** (чекліст подачі).
- [ ] Є **заява §4**: Product capabilities · third-party tools · AI tools.
- [ ] **Пітч однаковий** із README і описом репо (107 символів; поле
      *Elevator pitch* на сторінці 1 оновити на цей самий, воно досі містить
      старий 112-символьний — див. `devpost-submission-form.md`).
- [ ] **Жодних імен суддівської панелі** — за рішенням **V1** імена не
      зберігаються в репозиторії; шаблон пошуку тримати **поза** ним
      (у приватних нотатках), а не в цьому файлі.
- [ ] Числа збігаються з README: 1,667 · 3,730 · 600 · 553 · 1.1 MB · 12–17 s ·
      11 gates · 7 queries · 5 tools · 60+.

## Відкриті нотатки

1. **ШІ-голос у відео (§3, §4):** ✅ **ВИКОНАНО 27.11.2026** — плейсхолдер
   вище заповнено. Голос: **Kokoro-82M (Apache-2.0), локально на CPU** (не
   ElevenLabs — див. порівняння ліцензій у шот-листі). Заява тепер містить і
   розробку за участі ШІ, і ШІ-голос, і власну музику — тобто §4 закрито
   повністю. Крок39 вимагає подавати це **як інженерну дисципліну, а не
   виправдання** (D33).
2. **Фразеологія §3 уточнена:** у кроці39 перелік був записаний скорочено
   (*CLI, embedded use, MCP, or a connection to Neo4j or Aura*), а в правилах
   дослівно: *«for example through the CLI, embedded use, WebAssembly, MCP,
   Bolt or HTTP, hybrid retrieval, or a connection to Neo4j or Aura»*.
   Перелік «for example» = не вичерпний, тож скорочений підмножини
   достатньо; **WebAssembly і hybrid retrieval навмисно не згадуємо**
   (перший не використано — M3 відкладено; другий поза обсягом і не є
   пропуском, якщо мовчати).
3. **Не дублюємо README повністю:** опис = стратегічна історія
   (проблема → чому граф → аудований доказ → шлях адопції); повні таблиці,
   таймінги та обмеження лишаються в README і `docs/limitations.md`.
