# Devpost submission form — inventory (draft #1314206)

**Чернетка створена 21.11.2026.** ID `1314206`, slug `1314206-cascade`, статус **DRAFT**
(приватна — публічно нічого не видно). Submit **не** натискається до внутрішнього
дедлайну 9.12 (офіційний — 11.12, 18:00 PST ≈ 04:00 12.12 Київ).

Редагування: `https://devpost.com/submit-to/32024-relate-by-neo4j-hackathon/manage/submissions/1314206-cascade/project-overview`

Форма — візард із **3 сторінок** (зберігається кнопкою `Save & continue`):

## Сторінка 1 — Project overview

| Поле | Обов'язкове | Стан / план |
| --- | --- | --- |
| `* Project name` | так | ✅ **Cascade** (заповнено 21.11) |
| `* Elevator pitch` (textarea) | так | ✅ *«What breaks if we change this? One Cypher question instead of seven tables — with the exact graph path as proof.»* (112 символів, заповнено 21.11) |
| `Edit thumbnail` (file) | ні | ⬜ План: GIF/PNG із вьюера (крок 30) |

## Сторінка 2 — Project details (Project Story)

| Поле | Обов'язкове | План наповнення |
| --- | --- | --- |
| `* About the project` (textarea, markdown, placeholder `## Inspiration...`) | так | ⬜ З **README** (крок 39): Use case → How it uses Relate (mode / why / what the graph models) → Setup and run → Where the data lives → Limitations |
| `* Built with` (теги, select2) | так | ⬜ `relate`, `python`, `cytoscape`, `graph database`, `mcp` (крок 40) |
| `"Try it out" links` (URL) | ні | ⬜ `https://github.com/koztechie/cascade` (крок 40) |
| `Image gallery` (file, drag&drop) | ні | ⬜ Скріншоти вьюера (крок 32) |
| `* Video demo link` (YouTube/Vimeo URL) | так | ⬜ Відео 60–90 с (крок 28; завантажити ≈5.12) |

## Сторінка 3 — Submit (finalization)

| Елемент | Обов'язковий | Примітка |
| --- | --- | --- |
| Чекбокс `* I, and all of my team members, have read and agree to be bound by the Official Rules...` | так | Ставиться безпосередньо перед Submit |
| Кнопка **`Submit project`** | — | **Натиснути лише 9.12** (крок 50). Після Submit — перевірити статус (крок 51) |

## Що блокує Submit (перевірити 8.12, крок 47)

- `Project name`, `Elevator pitch` ✓ (заповнені)
- `About the project` — порожнє
- `Built with` — порожнє
- `Video demo link` — порожній
- Official Rules чекбокс — не позначений

## Технічні нотатки

- Захист від ботів: **reCAPTCHA invisible v2** на кнопках `Start project` / `Create project` — проходиться вручну (21.11 пройдено власноруч).
- Прямий URL форми (`/software/new`) не існує; вхід через `Start project` на сторінці конкурсу або `Create project` у менеджері: `devpost.com/submit-to/32024-relate-by-neo4j-hackathon/manage/submissions`.
- Ліміт elevator pitch перевірено на практиці: 112 символів приймаються.
