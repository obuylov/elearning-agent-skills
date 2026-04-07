---
name: analysis-scanner
description: "Оркестратор этапа анализа исходников: при необходимости запускает конвертацию, затем субагента-классификатора и формирует переход к следующему этапу."
---

# Analysis-Scanner — Оркестратор анализа исходников

## Inputs

- [project-state.json](../../../project-state.json) (статус проекта)
- Файлы в [sources/original/](../../../sources/original/) (.docx, .pdf, .pptx, .xlsx и др.)
- Файлы в [sources/converted/*.md](../../../sources/converted/) (если уже есть)

## Logic

### Шаг 0: Проверка статуса проекта

Прочитай [project-state.json](../../../project-state.json). Убедись, что скилл `start` выполнен.

### Шаг 1: Решение, нужна ли конвертация

Проверь папки [sources/original/](../../../sources/original/) и [sources/converted/](../../../sources/converted/).

- Если **в [sources/original/](../../../sources/original/) есть файлы**, а
  **[sources/converted/](../../../sources/converted/) пуста или не содержит соответствующих .md** —
  **запусти скилл `sources-converter`**.
- Если в [sources/converted/](../../../sources/converted/) уже есть актуальные `.md` (после предыдущих запусков
  или ручной конвертации) — **пропусти конвертацию**.
- Если обе папки пусты и в [project-state.json](../../../project-state.json) указан `source_mode: none` —
  пропусти конвертацию и передай это в субагент-классификатор, чтобы он сформировал минимальный отчёт.

### Шаг 2: Запуск субагента «Классификатор контента»

После (возможной) конвертации вызови скилл `content-classifier`:

1. Передай ему контекст проекта (из [project-state.json](../../../project-state.json)).
2. Дай доступ к всем `.md` в [sources/converted/](../../../sources/converted/).
3. Дождись завершения его работы и появления отчёта [workspace/sources-report.md](../../../workspace/sources-report.md).

Не дублируй внутри этого скилла логику чтения, классификации и записи отчёта — она полностью живёт в `content-classifier`.

### Шаг 3: Обновление [project-state.json](../../../project-state.json) и переход

1. Обнови [project-state.json](../../../project-state.json): отметь `analysis-scanner` → `completed`.
2. Покажи пользователю краткую сводку отчёта.
3. **Автоматически запусти** скилл `analysis-router`. Для пользователя это продолжение одного процесса — не спрашивай отдельного подтверждения.

## Outputs

- (Опционально) сконвертированные `.md` файлы в [sources/converted/](../../../sources/converted/), если был вызван `sources-converter`
- Файл [workspace/sources-report.md](../../../workspace/sources-report.md) — структурированный отчёт с YAML frontmatter
- Обновлённый [project-state.json](../../../project-state.json)
- **Автоматический запуск** `analysis-router`