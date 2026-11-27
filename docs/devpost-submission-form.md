# Devpost submission form — inventory (draft #1314206)

**Чернетка створена 21.11.2026. ✅ SUBMIT НАТИСНУТО 27.11.2026** — ID `1314206`,
slug `1314206-cascade`. **Публічна сторінка:** https://devpost.com/software/cascade-kys6m8
(HTTP 200, *«Submitted to Relate by Neo4j Hackathon»*, голосування до 16.12;
перевірено відкриттям сторінки 27.11). Редагувати можна аж до дедлайну (§4),
офіційний дедлайн — 11.12, 18:00 PST ≈ 04:00 12.12 Київ.

Редагування: `https://devpost.com/submit-to/32024-relate-by-neo4j-hackathon/manage/submissions/1314206-cascade/project-overview`

Форма — візард із **3 сторінок** (зберігається кнопкою `Save & continue`):

## Сторінка 1 — Project overview

| Поле | Обов'язкове | Стан / план |
| --- | --- | --- |
| `* Project name` | так | ✅ **Cascade** (заповнено 21.11) |
| `* Elevator pitch` (textarea) | так | ⚠️ **ОНОВИТИ ПЕРЕД ПОДАЧЕЮ:** у полі досі **старий** текст (112 символів, заповнено 21.11). Замінити на єдиний пітч із B2.2 — **107 символів** (ліміт форми насправді **200**, не 140 — лічильник 27.11 показував «112 used / 88 left»), той самий, що в README і в описі репо: *«Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.»* |
| `Edit thumbnail` (file) | ні | ⬜ План: GIF/PNG із вьюера (крок 30) |

## Сторінка 2 — Project details (Project Story)

| Поле | Обов'язкове | План наповнення |
| --- | --- | --- |
| `* About the project` (textarea, markdown, placeholder `## Inspiration...`) | так | 🟣 **ТЕКСТ ГОТОВ** — [`docs/devpost-description.md`](devpost-description.md) (B2.7, 23.11): 5 заголовків шаблону в порядку + окрема секція `What connects to what` + заява §4 (Product capabilities / third-party / AI tools). **✅ 27.11 дописано заяву про ШІ-голос** (Kokoro-82M, Apache-2.0, локально на CPU) — плейсхолдер «якщо у відео ElevenLabs» закрито, §4 тепер повний. Готовий файл для вставлення: `/mnt/data/devpost-gallery/about-the-project.md` (абзаци склеєні в один рядок — без випадкових переносів; перестворити: `python3 /mnt/data/devpost-gallery/make-paste.py`, скрипт сам перевіряє, що текст і рендери не змінилися). **Вставити вручну** — сесії в агента немає |
| `* Built with` (теги, select2) | так | ⬜ `relate`, `python`, `cytoscape`, `graph database`, `mcp` (крок 40) |
| `"Try it out" links` (URL) | ні | ⬜ `https://github.com/koztechie/cascade` (крок 40) |
| `Image gallery` (file, drag&drop) | ні | 🟣 **8 скріншотів ГОТОВІ 27.11** — `/mnt/data/devpost-gallery/01-question … 08-close.png`, усі **1920×1280 (3:2)**, смуги кольору фону `#0e1116`, 214–576 КБ (<5 МБ). Кадри знято з фінального відео (з озвучкою) на тайм-кодах 5/17/32/46/64/74/80.5/87 с. **Каптиони до кожного — готові:** `/mnt/data/devpost-gallery/captions.txt` (англійською, лише про те, що видно на кадрі; звірено з відео; **усі ≤140 символів** — найдовший 139). Завантажити вручну. **✅ GIF додано 27.11 → у галереї 9 елементів** (`video/viewer.gif`, **позиція 9**, після `08-close`; 720×406 · 60 кадрів · `loop=0` · 1 712 995 Б = 1.71 МБ < 5 МБ; підпис 88 символів; звірено з оригіналом на Cloudfront — MAE кадрів 0.00) |
| `* Video demo link` (YouTube/Vimeo URL) | так | ⬜ `https://youtu.be/EuO9WT4_lPc` — **але спочатку переконатись, що на YouTube версія З ОЗВУЧКОЮ** (коміт `ef56024`), і перемкнути visibility на **Public** |

## Сторінка 2а — Custom submission requirements (режим Relate)

Знайдено **27.11.2026** — окремий крок візарда між *Project details* і *Submit*.
**Усі 5 полів обов'язкові**, значення вже звірені з README і з репозиторієм.

| Поле | Значення для вставки | Звірка |
| --- | --- | --- |
| `* Public GitHub repo URL` | `https://github.com/koztechie/cascade` | ✅ **PUBLIC**, не архівовано, топіки `relate`, `relate-neo4j-hackathon`; HTTP 200 без авторизації (перевірено 27.11 через `gh repo view` + `curl`). Корінь репо, не підпапка — як просить hint |
| `* Which Relate mode does your project use?` (select) | **`Single file`** | ✅ README рядок 119: *«**Mode:** single file (`store/catalog.rl`)»* — дослівно |
| `* Path to the persistent store in your repo` | `store/catalog.rl` | ✅ файл у репо, **1 069 056 Б = 1.1 MB** (як у README), sha256 `01bc0816…` = закомічений стан |
| `* Why did you choose this mode?` (textarea, 1–2 речення) | **див. текст нижче** | ✅ слова взято з секції README *«How it uses Relate» → «Why this mode»*, як і вимагає hint |
| `* I confirm my repo is public and Relate is running in my code…` (чекбокс) | ✅ **ставити** | Твердження істинні: репо публічне ✓, Relate виконується в коді (`bin/relate`, `relate query`, `relate serve --mcp stdio`) ✓. Prompt-only entries не застосовуються |

**Текст для `* Why did you choose this mode?` (2 речення):**

```
One file is the whole database: judges can inspect it, commit it, move it, open it — no server and no directory to reconcile. The single 1.1 MB file carries the entire graph (1,667 nodes, 3,730 relationships), so the whole database travels with the repo.
```

*Чому саме так:* перше речення — дослівно з README (*«one file **is** the whole
database — judges can inspect it, commit it, move it, open it. No server, no
directory to reconcile»*), друге — із блоку *Portability*. Форма прямо каже
*«It should match the "How it uses Relate" section of your README»* — суддя
порівняє обидва місця, тож розбіжностей бути не повинно.

**✅ Поле режиму перевірено ззовні 27.11** (бо сама сторінка подачі його не
рендерить): галерея хакатону `https://relate.devpost.com/` має фільтр
*«Which Relate mode does your project use?»*, а пошук за ним —
`https://relate.devpost.com/submissions/search?utf8=✓&filter[which relate mode does your project use?][]=single file`
(сторінка 2) **містить `cascade-kys6m8`**. Звірка складу: single file 64 +
directory 24 + in memory 6 = **94 = кількість проєктів у галереї** → фільтр
надійний, наш режим — **`Single file`** ✓. *Поля `Path…` / `Why…` / чекбокс
ззовні не публікуються — вони обов'язкові, а подача пройшла, тож заповнені.*

## Сторінка 3 — Submit (finalization)

| Елемент | Обов'язковий | Примітка |
| --- | --- | --- |
| Чекбокс `* I, and all of my team members, have read and agree to be bound by the Official Rules...` | так | Ставиться безпосередньо перед Submit |
| Кнопка **`Submit project`** | — | **Натиснути лише 9.12** (крок 50). Після Submit — перевірити статус (крок 51) |

## Стан полів на момент Submit (звірено 27.11 із публічної сторінки)

- `Project name` ✓ `Cascade` · `Elevator pitch` ✓ **новий 107-символьний пітч** (`og:description` збігається з README)
- `About the project` ✓ 7 заголовків рендериться як `<h2>/<h3>`, сирого markdown немає; заява §4 із **Kokoro** на місці, *«seven tables»* / *ElevenLabs* відсутні
- `Built with` ✓ 5 тегів: `cytoscape`, `graph-database`, `mcp`, `python`, `relate`
- `Video demo link` ✓ `EuO9WT4_lPc` — **90 с**, `isUnlisted:false`, завантажене **27.11 15:00 UTC**, тобто **після** коміта озвучки `ef56024` (09:06 UTC) → версія з голосом
- `Image gallery` ✓ **9 елементів**: 8 скріншотів (1920×1280) + **GIF**
  `video/viewer.gif` (позиція 9, після `08-close`) — усі 9 із каптионами ≤140 ·
  обкладинка ✓ **3:2** (похідна 333×222 від нашого `thumbnail-devpost.png`)
- Official Rules чекбокс ✓ — сторінка у статусі submitted

**Відкриті пункти перед будь-яким редагуванням (крок 47/50):**
- ~~порядок галереї зворотний~~ → **✓ виправлено 27.11** (тепер 1 `01-question` → 8 `08-close`, перевірено повторним відкриттям сторінки)
- поля `* Which Relate mode` / `* Path to the persistent store` **на публічній сторінці не рендеряться** (0 збігів «Single file» у HTML) → звірити їх у manage-вигляді, бо ззовні підтвердити неможливо
- повторно прочитати Official Rules і шапку «Updated …»

## Технічні нотатки

- Захист від ботів: **reCAPTCHA invisible v2** на кнопках `Start project` / `Create project` — проходиться вручну (21.11 пройдено власноруч).
- Прямий URL форми (`/software/new`) не існує; вхід через `Start project` на сторінці конкурсу або `Create project` у менеджері: `devpost.com/submit-to/32024-relate-by-neo4j-hackathon/manage/submissions`.
- Ліміт elevator pitch перевірено на практиці: 112 символів приймаються.
