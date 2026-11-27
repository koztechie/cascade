# Share blurb — готовий текст для поширення (D55 · крок 32)

**Призначення:** копі-паст для **однієї** чесної публікації (крок 56) і для
статті dev.to (крок 55). Усе звірено з README і з відео — нічого не
вигадувати й не переписувати на льоту.

---

## 1. Теглайн (107 символів — ліміт заголовка 140)

```
Know the blast radius before it breaks: one Cypher question returns a path through the graph — not a score.
```

Той самий рядок, що в `README.md`, в описі репозиторію і в полі *Elevator
pitch* на Devpost. **Не змінювати** — суддя скрізь має бачити одне й те саме.

---

## 2. Готовий абзац для поширення (~80 слів)

```
What breaks if we stop selling one product? Cascade answers with one Cypher question instead of a ten-table join — and the answer arrives as a path through the graph (listing → product → category → feed contract), so the consequence is proven, not asserted. It runs on Relate as a single 1.1 MB file: 1,667 nodes, 3,730 relationships, no server, no signup. Inside: an offline browser viewer, eleven self-grading gates (make verify) and five read-only MCP tools for agents. Demo, 1:30 → https://youtu.be/EuO9WT4_lPc · Code → https://github.com/koztechie/cascade
```

---

## 3. Короткий варіант (для соцмереж, ≤280 символів)

```
"What breaks if we stop selling this?" — one Cypher question, one path as proof. Cascade runs on Relate as a single 1.1 MB file: no server, no signup, offline viewer + 5 read-only MCP tools. 1:30 demo → https://youtu.be/EuO9WT4_lPc
```

---

## 4. Правила (крок 56 — читати ДО публікації)

- **Одна** публікація. Без спаму, без повторів, без vote-циклів.
- **⚠️ Devpost ToS:** жодної **автоматизації** голосування (manual *or*
  automated) і жодної **компенсації** виборцям, навіть неявної («ти мені — я
  тобі») → ризик **дискваліфікації**. Організатори самі заохочують поширення
  в соцмережах → **одна чесна публікація = безпечно**.
- Посилання на подачу: `https://devpost.com/software/cascade-kys6m8`
  (публічна з 27.11; голосування до **16.12**).
- **Від першої особи**, без натяку на схвалення Neo4j нашого проєкту
  (правила §8 про бренд).
- Не згадувати імен суддівської панелі (рішення **V1**).

---

## 5. Звірка чисел (перечитати перед публікацією)

| Твердження | Де перевірено |
| --- | --- |
| 1.1 MB · 1,667 nodes · 3,730 relationships | README, `make check-claims` ✓ |
| ten-table join (10 таблиць) | `sql-contrast.html`: Product · Listing · Marketplace · Feed · Mapping · Category · Rule · Campaign · Page · Segment |
| eleven gates · `== verify: OK ==` | `scripts/verify.sh` (11 маркерів), прогін 27.11 exit 0 |
| five read-only MCP tools | `tools/list` живого сервера (`make check-claims`) |
| Demo 1:30 | YouTube `EuO9WT4_lPc`, `duration=90` |
| offline viewer, no server, no signup | `viewer.html` у репо, відкривається файлом |
