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
  `11 gates · 12–17 s on a 2013 floor machine`
- **Озвучка / субтитри (дослівно, `## Evidence and engineering proof`):**
  > Every number in this README comes from a run, not from typing.

---

## Сцена 1 — знімальний аркуш (крок 21)

**Перший кадр = питання** (вимога кроку 27) — картка готова:
[`scene1.html`](../scene1.html). Відкрити → `F11` на весь екран → знімати
**~15 с** (вікно сцени 1: 0:00–0:15).

### ✅ Знято 23.11.2026 — обидва дублі готові

| Файл | Параметри |
| --- | --- |
| `/tmp/opencode/scene1/scene1-take1.mp4` | h264 · **1920×1080** · 30 fps · **15.000 с** · 149 КБ (fade 0.5 с) |
| `/tmp/opencode/scene1/scene1-take2.mp4` | h264 · 1920×1080 · 30 fps · **15.000 с** · 180 КБ (fade 0.8 с) |
| `/tmp/opencode/scene1/scene1-frame.png` | перший кадр 1920×1080 — постер/прев'ю |

**Метод — не запис екрана, а рендер.** Знімати робочий стіл **не став**:
у кадрі на той момент були відкриті робочі й особисті вікна (шляхи,
підключення, файли) — **саме те, що §11 і крок 17 забороняють показувати**, а
на переходах (запуск/закриття браузера) стіл з'явився б у кадрі на частку
секунди. Замість цього картку **відрендерено головно** → у кадрі **взагалі
немає десктопу**, кроп не потрібен, розмір рівно 1080p.

**Повторити (файли відтворювані, одна команда):**
```bash
cd <repo>
python3 -c "
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    pg=b.new_page(viewport={'width':1920,'height':1080})
    pg.goto(Path('scene1.html').resolve().as_uri()); pg.wait_for_timeout(300)
    pg.screenshot(path='scene1-frame.png'); b.close()"
ffmpeg -y -loop 1 -i scene1-frame.png -t 15 -r 30 \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=14.5:d=0.5,format=yuv420p" \
  -c:v libx264 -crf 18 -movflags +faststart scene1-take1.mp4
```
*Потрібен `python3 -m playwright install chromium` (одноразово, 114 МіБ) —
системний Chrome на цій машині зламаний (`crashpad`, exit 133).*

| Елемент | Текст (дослівно) |
| --- | --- |
| Заголовок | `We are discontinuing PU-1004 — what breaks?` |
| Підрядок | `Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.` |

- **Мова кадру — англійська.** Судді англомовні, а критерій Clarity оцінює
  прямо *«quality of the written explanation, demo, and visual presentation»*.
  Український рядок із кроку 21 — скорочення плану, **не текст для кадру**.
- **Озвучка під кадр** (дослівно з README, `## Use case`):
  > The blast radius of that one change is scattered across product feeds,
  > marketplace listings, price rules, campaigns, landing pages and CRM
  > segments — today it lives in spreadsheets and tribal knowledge, and nobody
  > finds the seventh consequence until it breaks.
- **Дублі:** крок 25 вимагає ≥1, але зафіксувати **2** — на випадок збою.
- **Палітра:** картка бере `--bg / --text / --muted / --accent` із
  `viewer.html` → кадр виглядає як частина проєкту, а не чужий слайд.
- **Перед зйомкою:** робочий стіл кропимо (крок 17), у кадрі немає особистих
  даних інших людей (§ 11).

### ⚠️ Розбіжність структур сцен — вирішити ДО кроку 22

| План (кроки 21–25) | Шот-лист (крок 19, за D1) |
| --- | --- |
| 1. питання | 1. проблема + картка ← **питання і є першим кадром (крок 27)** |
| 2. `make verify` → 475 | 2. шлях-доказ (`viewer.html`) |
| 3. SQL-контраст | 3. агент через MCP |
| 4. агент | 4. нетехнічний читач (`make report`) |
| 5. вьюер | 5. `make verify` |

**Рекомендація — триматися шот-листа**, і ось чому:

1. **D1 позначено `[8/8]`** і задає саме цей порядок: проблема → шлях-доказ →
   агент → нетехнічний → `make verify`. Шот-лист написаний під нього.
2. **Крок 22 технічно хибний:** `make verify` **не друкує 475 рядків** —
   це вивід запиту `01` із `make demo`. Верифікація і blast radius — різні
   команди; на одному кадрі їх не поєднати.
3. **Крок 23 суперечить опублікованому README:** у плані *«7 таблиць і
   7 JOIN'ів»*, а в README (звірено в B2.6) — **ten tables** (10 таблиць).
   Виводити «7» на екран = суперечність із нашим же твердженням, яке перевіряє
   `check-claims`.
4. **SQL-контраст не потребує окремої сцени** — як підрядок сцени 2
   («one pattern here, ten tables there»), він уже є в README.
   *(**Станом на 23.11.2026 цю рекомендацію замінено рішенням:** картку
   відзнято і **вставляти будемо** — див. секцію «Сцена 3 (крок 23)»; бюджет
   105 с ≤ 120 с.)*

*Якщо обираєш планівський порядок — переписати шот-лист ДО зйомки сцен 2–5,
щоб титри й озвучка не розійшлися.*

## Сцена 2 — знімальний аркуш (крок 22)

### ⚖️ Рішення прийнято: триматися шот-листа (підпункт кроку22 закрито)

Обґрунтування **виміряне, не припущене**:

1. **D1 позначено `[8/8]`** і задає порядок: проблема → шлях-доказ → агент →
   нетехнічний → `make verify`. Шот-лист написаний під нього.
2. **Крок 22 не виконується на екрані:** гейт `01` у `verify.sh` викликає
   `query_out 15` → `sed -n "1,15p"`, тобто **друкує лише 15 із 475 рядків**.
   Побачити 475 можна лише з `make demo`. Тобто титул обіцяє те, чого в кадрі
   не буде.
3. **Крок 23 суперечить README:** у плані «7 таблиць і 7 JOIN'ів», а в README
   (звірено в B2.6) — **ten tables**. На екран виводити «7» не можна.

### ✅ Знято 23.11.2026 — обидва дублі готові

| Файл | Параметри |
| --- | --- |
| `/tmp/opencode/scene2/scene2-take1.mp4` | h264 · **1920×1080** · 30 fps · **20.000 с** · 368 КБ |
| `/tmp/opencode/scene2/scene2-take2.mp4` | h264 · 1920×1080 · 30 fps · **20.000 с** · 319 КБ |

**Дублі справжні:** кожен записувався окремим завантаженням, а `cose`-розкладка
має `randomize:true` → **позиції вузлів різні** (перевірено порівнянням кадрів).

### Що у кадрі (перевірено візуально)

- шапка: *Focus product* **PulseKit Sneakers Edge Sand** · **130 nodes · 142
  relationships** · «every edge is a real relationship in `store/catalog.rl`»;
- **клік по фокус-вузлу** → усе гасне, **фокус-кластер підсвічується**, панель
  справа перераховує шляхи: `HAS_BRAND → PulseKit` · `SUPPLIED_BY → Baltic
  Freight OU` · `IN_CATEGORY → Sneakers` · **`FEATURES ← Page: /p/pu-1004`** ·
  **два `OFFERS ← …/pu-1004`**;
- **зв'язок зі сценою1 є:** картка каже «discontinuing **PU-1004**», а в панелі
  видно `/p/pu-1004` і лістинги `…/pu-1004`.

### 🔍 Два факти, знайдені під час зйомки

1. **`PU-1004` = `PulseKit Sneakers Edge Sand`** (перевірено запитом до
   магазину: `sku=PU-1004`, `name=PulseKit Sneakers Edge Sand`). У вузлі
   **SKU не показується** — лише назва; саме тому SKU видно тільки в
   сусідніх вузлах (`/p/pu-1004`, лістинги). Якщо захочеш сильнішого
   зв'язку — додати титр із SKU поверх кадру на кроці 26.
2. **`playwright`-відео НЕ захоплює canvas** у headless-shell: запис був
   порожнім (лише шапка), хоча **знімок показував граф** (130 вузлів,
   41 032 світлих пікселів). Тому знято **послідовністю знімків** → `ffmpeg`.
   Виявилось, що в межах фази кадри **ідентичні** (0 пікселів різниці), а
   перехід дає **62 334 пікселі** → закодовано **плавно на 30 fps** з
   реальних кадрів.

**Повторити:** той самий скрипт (у `PLAN64`, крок 22) — послідовність
знімків 4 с до кліку + 16 с після, `ffmpeg -framerate <fps> -vf "fps=30"`.

## Сцена 3 (крок 23) — SQL-контраст

### ⚠️ Число в титулі виправлено: «7 таблиць» → **ten tables**

Титул кроку23 — *«у SQL це 7 таблиць і 7 JOIN'ів»* — **не має підстав** у
наших опублікованих твердженнях. Перелік у README (секція
**«Cypher next to the SQL it replaces»**) **пораховано скриптом: рівно 10**
(`Product · Listing · Marketplace · Feed · Mapping · Category · Rule ·
Campaign · Page · Segment`), і README прямо каже **«ten tables»** — це
твердження охороняє `check-claims` через B2.6. На екран виводити «7» означало б
**суперечність із власним README**. Тому на картці — **ten tables**.

### ✅ Знято 23.11.2026 — обидва дублі готові

| Файл | Параметри |
| --- | --- |
| `/tmp/opencode/sql/sql-take1.mp4` | h264 · **1920×1080** · 30 fps · **15.000 с** · 220 КБ (fade 0.5 с) |
| `/tmp/opencode/sql/sql-take2.mp4` | h264 · 1920×1080 · 30 fps · **15.000 с** · 241 КБ (fade 0.8 с) |

Джерело: [`sql-contrast.html`](../sql-contrast.html) — та сама палітра, що в
`viewer.html` / `scene1.html`; **0 JS, 0 зовнішніх ресурсів**.

**Що у кадрі (перевірено візуально):** заголовок *«Ten tables in SQL. **One
pattern in Cypher.**»* → дві панелі: **SQL** = `10 tables` + повний перелік
із 10 назв + «joined with a recursive CTE for every hop» · **Cypher** =
`1 pattern` (query `01`, one variable-length traversal).

### 📌 Статус у структурі відео — РІШЕННЯ ПРИЙНЯТО (23.11.2026)

Ця сцена — **додатковий вставка-кадр**, а не частина з п'яти основних сцен
шот-листа (рішення кроку22: шот-лист визначає порядок).
**✅ ВСТАВЛЯТИ у фінальну склейку (крок 26).**

**Бюджет:** основні сцени 1–5 = **90 с** (0:00–1:30) + вставка **15 с** =
**105 с** ≤ ліміт §4 **120 с** ✓.
**Правило на випадок перевищення:** якщо фактична склейка >120 с — першою
прибрати саме цю вставку (вона єдина необов'язкова), а не різати основні
сцени.

**Повторити:**
```bash
python3 -c "
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    pg=b.new_page(viewport={'width':1920,'height':1080})
    pg.goto(Path('sql-contrast.html').resolve().as_uri()); pg.wait_for_timeout(400)
    pg.screenshot(path='sql-frame.png'); b.close()"
ffmpeg -y -loop 1 -i sql-frame.png -t 15 -r 30 \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=14.5:d=0.5,format=yuv420p" \
  -c:v libx264 -crf 18 -movflags +faststart sql-take1.mp4
```

## Сцена 4 плану = сцена 3 шот-листа — Агент через MCP (крок 24)

**Позиція:** 0:35–0:55 · **20 с** · 1 команда + 1 екран.

### ✅ Знято 23.11.2026 — обидва дублі готові

| Файл | Параметри |
| --- | --- |
| `/tmp/opencode/scene4/scene4-take1.mp4` | h264 · **1920×1080** · 30 fps · **20.000 с** · 425 КБ (темп 4/5/11 с) |
| `/tmp/opencode/scene4/scene4-take2.mp4` | h264 · 1920×1080 · 30 fps · **20.000 с** · 426 КБ (темп 3/6/11 с) |

**Дублі = дві монтажні версії** з різним темпом (контент детермінований —
той самий живий транскрипт).

### У кадрі — СПРАВЖНІЙ MCP-обмін, не макет

Дані знято **живим викликом** `./bin/relate serve --mcp stdio --read-only`:
`initialize` → `tools/list` → `tools/call read_cypher`. Відповідь — **2 рядки
× 4 хопи**:

```
Listing:  https://rozetka.example/pu-1004
Product:  PulseKit Sneakers Edge Sand
Category: Sneakers
Mapping:  gtin
Feed:     Google Merchant Center
```

(другий рядок — той самий шлях для `google-shopping.example/pu-1004`.)

**Три стани в таймлайні** (наростання перевірено: 21 432 → 40 642 → 57 136
світлих пікселів):
1. **0–4 с** — команда `serve --mcp stdio … --read-only` + «connected — 5
   read-only tools» (`read_cypher · get_schema · blast_radius ·
   rejection_causes · remediation`);
2. **4–9 с** — питання *«We are discontinuing PU-1004 — what breaks?»* + виклик
   `read_cypher` із реальним Cypher;
3. **9–20 с** — `→ 2 rows · 4 hops` і обидва шляхи.

### Титр D5 (у кадрі, нижня третина)

> **Read-only and bounded — a deliberate choice.** For an analytics tool,
> refusing every write is a stronger guarantee than promising not to clobber:
> **it cannot delete anyone's graph, including yours.**

**Де лежить те саме речення в текстах:** буліона *«Share graph state safely…
without clobbering»* **у наших документах немає** (перевірено grep'ом — це
захищене копірайт-обладнання Relate на сторінці конкурсу), тому речення D5
**додано в README**, у `## For your agent`, одразу після блоку команди
`serve`. Воно спирається на те, що вже перевірено: `make verify` (гейт `05`)
**саме це і тестує** — що запис відмовляється.

**Повторити:**
```bash
python3 /tmp/opencode/scene4/build_stages.py     # 3 PNG з mcp.json
ffmpeg -loop 1 -t 4 -i stage1.png -loop 1 -t 5 -i stage2.png -loop 1 -t 11 -i stage3.png \
  -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0,fps=30,format=yuv420p" \
  -c:v libx264 -crf 18 -movflags +faststart scene4-take1.mp4
```

## Крок 20 — демо-стейт (репетиція пройдена 23.11.2026)

**Прогін у свіжій оболонці (`bash --noprofile --norc`): усі сцени
виконались без зупинок, робоче дерево лишилось чистим.** Факти з прогону:

| Сцена | Виміряно |
| --- | --- |
| 2 · `viewer.html` | файл є, 29 212 байт |
| 3 · `serve --mcp stdio` | **чекає на stdin** — в інтерактивному терміналі EOF не настає, тож у кадрі зависне |
| 4 · `make report` | **~14 с** · **107 рядків** · шлях у **рядку 2**, `**Verdict:**` у **рядку 13** |
| 5 · `make verify` | **12–17 с** (два заміри: 12.16 і 16.71) · `FAIL=0` |

### Підготовка перед записом

1. **Свіжий термінал** — нове вікно, `clear`, жодного зайвого вкладення.
2. **Закрити зайве** — редактор, браузерні вкладки, чати, `PLAN64`. У кадрі:
   термінал (і `viewer.html` окремим вікном для сцени 2).
3. **Команди набрати заздалегідь, але НЕ запускати** — щоб у кадрі не було
   пауз на друкуванні:
   ```bash
   cd cascade
   make report     # сцена 4
   make verify     # сцена 5
   ```
4. **Сцену 3 не запускати «на порожньо»** — `serve` чекатиме вічно. Обрати
   одне: (а) показати вже запущений сервер у фоні, (б) запустити → одразу
   `Ctrl+C`, (в) знімати готову відповідь агента з
   [`docs/agent-session.md`](agent-session.md).
5. **Шлях у виводі:** `make report` / `make verify` друкують абсолютний шлях
   (`/mnt/data/…`) у рядках 2–3. **Він не містить імені чи домашньої теки** —
   це прикраса, не витік. За потреби обрізати при монтажі; **на це не
   витрачати час** (R6: розбірливість важливіша за полірування).
6. **Таймінг сцени 5:** `verify` виходить до 17 с при 18 с вікна — тісно.
   Якщо в кадрі довше — **подовжити сцену 5 до 20 с** (разом ≈92 с; ліміт
   правил — 120 с, запас є).

### ⚠️ Правило безпеки прогону (не повторювати помилку підготовки)

Під час підготовки я прокрутив `make verify | head -3`: `head` закрив трубу
після трьох рядків, `make` отримав **SIGPIPE посеред запису магазину**, і
`store/catalog.rl` зник. Відновлено з коміту (`sha01bc0816…` збігся),
гейти зелені. **Не додавати `| head` / `| tail` до цілей `make`** — друкувати
у файл або дивитися без переривання.

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
