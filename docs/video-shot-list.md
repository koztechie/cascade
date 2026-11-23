# Відео — сценарій-шот-лист (крок 19)

**Формат:** 5 сцен · **60–90 с** · кожна сцена = **1 команда АБО 1 екран**.
**Жорстке правило:** титри та озвучка — **дослівно з фінальних формулювань B2**
(текст у цьому файлі вже звірений із README станом на 23.11.2026).
**Переписати README після зйомки = перезняти відео.**

---

## Сцени

### 1 · Проблема людини — 0:00–0:15 · **1 екран** (титульна картка)

- **На екрані (титр, великим):**
  `Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.`
- **Озвучка / субтитри (дослівно з README, `## Use case`):**
  > The blast radius of that one change is scattered across product feeds,
  > marketplace listings, price rules, campaigns, landing pages and CRM
  > segments — today it lives in spreadsheets and tribal knowledge, and nobody
  > finds the seventh consequence until it breaks.
- **Команди немає** — суто текст. Чиста картка, без логотипів сторонніх служб.

### 2 · Шлях-доказ — 0:15–0:35 · **1 екран** (`viewer.html`)

- **Екран:** `viewer.html` — відкрити вже готовий граф (файл збірний, сервера
  немає). Клацнути вузол `PU-1004`, щоб ізолювати його ребра.
- **Титр (низ, стисло — бізнес-словами, не Cypher):**
  `PU-1004 → 2 listings → 1 page → 1 feed contract`
- **Озвучка / субтитри (дослівно, `## Why a graph`):**
  > every answer arrives as a **path** — so the consequence is proven, not
  > asserted.
- **⚠️ D10: показувати ШЛЯХ, а не таблиці.** «Ось ланцюжок, ось чому це
  ламається» — жодних знімків таблиць зі звіту в цій сцені.
- **⚠️ Контрольна точка Z8 на 0:30:** глядач **без технічної освіти** має
  вже розуміти дві речі: *про що це* (вибуховий радіус зміни) і *що показано*
  (шлях у графі, пояснений бізнес-словами). Якщо ні — переставити сцену 4
  на 0:20 і перезняти лише перші дві.

### 3 · Агент через MCP — 0:35–0:55 · **1 команда**

- **Команда в кадрі:**
  ```bash
  ./bin/relate serve --mcp stdio --database store/catalog.rl --read-only
  ```
- **На екрані:** термінал агента з питанням і відповіддю:
  `We are discontinuing PU-1004 — what breaks?` → відповідь із шляхами.
- **Титр:**
  `five read-only tools: read_cypher · get_schema · blast_radius · rejection_causes · remediation`
- **Озвучка / субтитри (дослівно, `## Why a graph`):**
  > the agent gets **connected context instead of a guess**, and every
  > sentence it says back can be checked against the edge that produced it.
- **Підготувати заздалегідь:** агент уже підключений через
  [`.mcp.json`](.mcp.json) з кореня репозиторію — у кадрі нічого не дротити.

### 4 · Нетехнічний читач — 0:55–1:12 · **1 команда**

- **Команда в кадрі:**
  ```bash
  make report
  ```
- **На екрані:** рядок `**Verdict:**` — перший вміст звіту (не таблиці).
- **Титр:**
  `one-line verdict → paste into a ticket`
- **Озвучка / субтитри (дослівно, `### What a non-technical person sees`):**
  > No Cypher required — the graph in business words: a product sits in a
  > category; it has listings on marketplaces; each feed demands certain
  > fields (a missing `gtin` gets a listing rejected); rules and campaigns
  > point at categories; pages link products and categories.
- **Тріада конкурсу (B2.10), якщо вистачить часу — одним рядком:**
  > `agents, apps, or people` … `One store, one set of paths, three ways in.`

### 5 · Довіра — 1:12–1:30 · **1 команда**

- **Команда в кадрі:**
  ```bash
  make verify
  ```
- **На екрані:** фінальний рядок `== verify: OK ==` (кінець виконання).
- **Титр:**
  `11 gates · 12 s on a 2013 floor machine`
- **Озвучка / субтитри (дослівно, `## Evidence and engineering proof`):**
  > Every number in this README comes from a run, not from typing.

---

## Правила §4 (офіційні правила, дослівно — звірено 23.11.2026)

- **«A demo: a video of up to 2 minutes»** → наші 60–90 с ✓.
- **«it must be your own work, including filming, editing, and graphic design»**
  → усе, що в кадрі, знімаємо, монтуємо і малюємо самі.
- **«Music, images, and other third-party material in the video must be used
  with permission»** → стороння музика/зображення **лише з дозволу**; за
  сумніву — **без музики взагалі** (субтитри + власний голос).
- **«The video must be accessible to judges without a login or payment»** →
  **завантажувати нативно в Devpost**, а не посиланням на закритий сервіс.
- У submission додати заяву: **Product capabilities · third-party tools ·
  AI tools** (текст уже готовий — `docs/devpost-description.md`).

## ElevenLabs — ліцензія озвучки (звірено з help center, 23.11.2026)

| План | Комерційне використання | Атрибуція |
| --- | --- | --- |
| **Платний** (Starter і вище) | **так**, необмежено в часі (генерації підписки лишаються правомочними і після скасування) | за вашою угодою |
| **Безкоштовний** | **ні** — *«the free plan does not include a commercial license and cannot be used for any commercial purpose»* | обов'язково `elevenlabs.io` у назві |

**Правило прийняття рішення:** платний план → озвучка дозволена, і голос
**задекларувати в submission** (§4 вимагає описати значне використання ШІ).
Безкоштовний або сумнів → **fallback**: живий мікрофон (перевірений у кроці 18)
**або лише субтитри**. Джерело: `elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform`.

## Планка монтажу (R6)

Організатори прямо пишуть **«A screen share or presentation is fine»** →
пріоритет — **розбірливість і структура сцен**, а не полірування.
За браку часу **зрізаємо за R6**: спершу GIF-обкладинка, потім сцени1–5;
**не дороблюємо графіку.**

## Що НЕ показувати (V3/V8/V11)

`PLAN64.md` · `docs/competitor-analysis.md` · `docs/refactoring.md` ·
`.github/workflows/` · внутрішні кроки рефакторингу та CI.
Також **не показувати повний шлях до теки** в терміналі — у кадрі хай буде
лише `cd cascade`.

## Після зйомки (кроки 24–28)

1. Завантажити **нативно в Devpost** (поле `* Video demo link` → URL відео
   на Devpost/YouTube/Vimeo, доступний без логіна).
2. Перевірити: тривалість ≤2 хв · субтитри читаються · жодного показаного
   файлу зі списку «Що НЕ показувати».
3. У submission — заява про згенерований голос (якщо використано).
