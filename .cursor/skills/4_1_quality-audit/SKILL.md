---
name: quality-audit
description: "Оркестрация аудита качества курса через субагентов. Спрашивает пользователя: запустить все 5 проверок или конкретные. Каждая проверка — отдельный фоновый субагент. Используй после завершения генерации контента или когда пользователь просит провести аудит, ревью или проверку качества курса."
---

# Quality-Audit — Оркестрация аудита качества

## Inputs

- [project-state.json](../../../project-state.json) (статус проекта)
- [content/pages/*.yaml](../../../content/pages/) (все собранные страницы курса)
- [workspace/brief.md](../../../workspace/brief.md) (бриф — требования, редполитика, аудитория)
- [workspace/sources-report.md](../../../workspace/sources-report.md) (аудит исходников)
- [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) (структура и матрица курса)

## Субагенты

| Файл                                                                                 | Имя                    | Режим      | Проверка              |
| ------------------------------------------------------------------------------------ | ---------------------- | ---------- | --------------------- |
| [`.cursor/agents/audit-completeness.md`](../../agents/audit-completeness.md)         | audit-completeness     | background | Полнота контента      |
| [`.cursor/agents/audit-brief-compliance.md`](../../agents/audit-brief-compliance.md) | audit-brief-compliance | background | Соответствие брифу    |
| [`.cursor/agents/audit-methodology.md`](../../agents/audit-methodology.md)           | audit-methodology      | background | Методическое качество |
| [`.cursor/agents/audit-accuracy.md`](../../agents/audit-accuracy.md)                 | audit-accuracy         | background | Фактическая точность  |
| [`.cursor/agents/audit-technical.md`](../../agents/audit-technical.md)               | audit-technical        | background | Техническое качество  |

## Logic

### Шаг 0: Проверка статуса проекта

Прочитай [project-state.json](../../../project-state.json).

1. Убедись, что генерация контента завершена (хотя бы `generation-text` выполнен).
2. Проверь `_active`: если установлен generation-скиллом — предупреди пользователя:
   > «Сейчас выполняется {_active.skill}. Аудит может дать неполные результаты. Дождитесь завершения генерации или подтвердите запуск аудита.»
3. Установи `_active`:

```yaml
_active:
  skill: quality-audit
  started: "{ISO timestamp}"
  checks_total: {количество выбранных проверок}
  checks_done: 0
```

### Шаг 1: Выбор проверок

Спроси пользователя:

> Какие проверки запустить?
> 1. **Все** — запустить все 5 проверок параллельно
> 2. **Полнота контента** — все ли блоки заполнены, нет ли заглушек
> 3. **Соответствие брифу** — tone of voice, обращение, уровень аудитории
> 4. **Методическое качество** — учебные цели, последовательность, фидбеки
> 5. **Фактическая точность** — соответствие исходникам, нет ли выдуманных фактов
> 6. **Техническое качество** — YAML-валидность, уникальность ID, обязательные поля

Пользователь может выбрать одну, несколько или все проверки.

### Шаг 2: Подготовка контекста

Собери необходимый контекст для выбранных субагентов:

| Субагент | Что передать в промте |
|----------|-----------------------|
| audit-completeness | Список файлов [content/pages/*.yaml](../../../content/pages/) |
| audit-brief-compliance | Содержимое [workspace/brief.md](../../../workspace/brief.md) + список файлов [content/pages/*.yaml](../../../content/pages/) |
| audit-methodology | Содержимое [workspace/brief.md](../../../workspace/brief.md) + [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) + список файлов [content/pages/*.yaml](../../../content/pages/) |
| audit-accuracy | `source_mode` из [project-state.json](../../../project-state.json) + [workspace/sources-report.md](../../../workspace/sources-report.md) + список файлов в [sources/converted/](../../../sources/converted/) + список файлов [content/pages/*.yaml](../../../content/pages/) |
| audit-technical | Список файлов [content/pages/*.yaml](../../../content/pages/) |

> **Важно:** Не вставляй содержимое всех страниц в промт — передавай только пути к файлам. Субагенты сами прочитают файлы.

### Шаг 3: Запуск субагентов

Запусти выбранные субагенты **в фоне** и **параллельно** (все в одном сообщении).

Для каждого субагента сформируй промт:

```
Проведи проверку "{название проверки}" для курса.

{контекст из Шага 2}

Файлы страниц в [content/pages/](../../../content/pages/):
{список файлов}
```

### Шаг 4: Сбор результатов

Дождись завершения всех запущенных субагентов. Каждый субагент записал свой отчёт в отдельный файл в [workspace/audit/](../../../workspace/audit/):

| Субагент | Файл отчёта |
|----------|-------------|
| audit-completeness | `workspace/audit/completeness.yaml` |
| audit-brief-compliance | `workspace/audit/compliance.yaml` |
| audit-methodology | `workspace/audit/methodology.yaml` |
| audit-accuracy | `workspace/audit/accuracy.yaml` |
| audit-technical | `workspace/audit/technical.yaml` |

Прочитай все созданные файлы из [workspace/audit/](../../../workspace/audit/) и собери сводную статистику.

### Шаг 5: Отчёт пользователю

Покажи сводку аудита:
- Всего страниц проверено: N
- Проверок выполнено: N из 5
- Критических проблем: N
- Серьёзных проблем: N
- Мелких замечаний: N

Перечисли **все критические** и **серьёзные** проблемы с описанием.
Мелкие замечания — только количество (полный список в [workspace/audit/](../../../workspace/audit/)).

### Шаг 6: Обновление [project-state.json](../../../project-state.json) и подтверждение

1. Удали `_active` из [project-state.json](../../../project-state.json).
2. Обнови [project-state.json](../../../project-state.json): отметь `quality-audit` → `completed`.
3. Спроси подтверждение перехода к скиллу `quality-fix`.
4. Не переходи без явного согласия пользователя.

## Outputs

- Файлы отчётов в [workspace/audit/](../../../workspace/audit/) — по одному на каждую проверку
- Обновлённый [project-state.json](../../../project-state.json)
- Сводный отчёт для пользователя
- Направление на `quality-fix`
