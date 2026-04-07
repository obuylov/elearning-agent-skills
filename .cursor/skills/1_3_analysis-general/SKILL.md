---
name: analysis-general
description: Методологический анализ и брифование на основе трёхосевой модели. Загружает ассеты по бизнес-драйверу (зачем), категории курса (что) и аудитории (для кого), проводит анализ, уточняет детали, собирает общие параметры и финализирует бриф.
---

# Analysis-General — Методологический анализ и брифование

> **Назначение.** Этот скилл ведёт основную часть брифования. Бизнес-драйвер, категория курса и аудитория уже определены скиллом `analysis-router`. Скилл загружает три набора ассетов (по каждой оси) и комбинирует их с универсальными вопросами. Для пользователя — продолжение непрерывной беседы.


## Inputs

- [project-state.json](../../../project-state.json) (статус проекта, `business_driver`, `course_category`, `target_audience`)
- [workspace/sources-report.md](../../../workspace/sources-report.md) (отчёт сканера)
- [workspace/brief.md](../../../workspace/brief.md) (если существует — дополнить, если нет — создать)

## Ассеты

### По бизнес-драйверу (зачем):

| Драйвер | Файл |
|---------|------|
| `compliance` | [`assets/drivers/compliance.yaml`](assets/drivers/compliance.yaml) |
| `rollout` | [`assets/drivers/rollout.yaml`](assets/drivers/rollout.yaml) |
| `performance` | [`assets/drivers/performance.yaml`](assets/drivers/performance.yaml) |
| `onboarding` | [`assets/drivers/onboarding.yaml`](assets/drivers/onboarding.yaml) |
| `knowledge` | [`assets/drivers/knowledge.yaml`](assets/drivers/knowledge.yaml) |

Содержит: определение, диагностику, WHY-вопросы, шаблон секции брифа, принципы проектирования, стратегию оценки.

### По категории курса (что):

| Категория | Файл |
|-----------|------|
| `processes` | [`assets/categories/processes.yaml`](assets/categories/processes.yaml) |
| `products` | [`assets/categories/products.yaml`](assets/categories/products.yaml) |
| `hardskills` | [`assets/categories/hardskills.yaml`](assets/categories/hardskills.yaml) |
| `softskills` | [`assets/categories/softskills.yaml`](assets/categories/softskills.yaml) |
| `business` | [`assets/categories/business.yaml`](assets/categories/business.yaml) |

Содержит: определение, фокусы анализа исходников, WHAT-вопросы, шаблон секции брифа, рекомендованные блоки.

### По аудитории (для кого):

| Аудитория | Файл |
|-----------|------|
| `frontline` | [`assets/audiences/frontline.yaml`](assets/audiences/frontline.yaml) |
| `managers` | [`assets/audiences/managers.yaml`](assets/audiences/managers.yaml) |
| `newcomers` | [`assets/audiences/newcomers.yaml`](assets/audiences/newcomers.yaml) |
| `experts` | [`assets/audiences/experts.yaml`](assets/audiences/experts.yaml) |
| `external` | [`assets/audiences/external.yaml`](assets/audiences/external.yaml) |
| `all_employees` | [`assets/audiences/all_employees.yaml`](assets/audiences/all_employees.yaml) |

Содержит: определение, характеристики аудитории, WHO-вопросы, шаблон секции брифа, рекомендации по дизайну (язык, структура, оценка, тон).

### Справочное:

| Файл | Назначение |
|------|------------|
| [`references/matrix.yaml`](references/matrix.yaml) | Матрица 5×5 с примерами для каждой ячейки |
| [`references/brief-general-template.yaml`](references/brief-general-template.yaml) | Шаблон общих параметров курса |

## Logic

**Управление состоянием (Micro-states):**
В процессе работы ты должен обновлять поле `analysis_general_stage` внутри файла `project-state.json`. Оно принимает значения: `init` → `driver_why` → `category_what` → `audience_who` → `general_params` → `final`. 
В этом же файле используй два дополнительных объекта:
1. `parked_knowledge`: массив, куда ты должен сохранять комментарии эксперта, если они относятся к будущим шагам (например, эксперт заговорил про аудиторию на шаге драйвера). Чтобы не ломать скрипт, скажи: *"Зафиксировал информацию про аудиторию, вернемся к этому позже"*, и сохрани это в парковку.
2. `current_brief_draft`: объект с ключами `driver`, `category`, `audience`, `general`. Записывай согласованные с пользователем куски брифа сюда (в оперативную память статуса), а не в `brief.md`.

Физически в файл `brief.md` мы будем писать строго один раз в самом конце (на Шаге 5).

### Шаг 0: Инициализация и проверка статуса (`stage: init`)
1. Прочитай [project-state.json](../../../project-state.json). Убедись, что `analysis-router` выполнен. Если `analysis_general_stage` не задано, установи его в `init`. Обнови статус, добавив поля `parked_knowledge: []` и `current_brief_draft: {}`, если их нет.
2. Извлеки `business_driver`, `course_category` и `target_audience`.
3. Переходи к Шагу 1.

### Шаг 1: Ось Y — Бизнес-драйвер (`stage: driver_why`)
1. Обнови стейт на `driver_why`. Загляни в `parked_knowledge`, вдруг там уже есть ответы по теме.
2. Загрузи файл `assets/drivers/{business_driver}.yaml`.
3. Проведи предварительную диагностику (Mager & Pipe, ADKAR и т.д.), описанную в поле `preliminary_diagnostics` файла. 
4. Задавай **WHY-вопросы** (`clarification_questions`).
5. **Ленивое сохранение:** После получения ответов, аккуратно заполни поле `current_brief_draft.driver` в `project-state.json`, следуя структуре `brief_template` из загруженного YAML-файла.
6. Переходи к Шагу 2.

### Шаг 2: Ось X — Категория и исходники (`stage: category_what`)
1. Обнови стейт на `category_what`. Загляни в `parked_knowledge`.
2. Загрузи файл `assets/categories/{course_category}.yaml`. 
3. Загляни в статус, проверь `source_mode`. Если он `full` или `partial` — проанализируй сконвертированные исходники в `sources/converted/` с фокусом на `source_analysis_focus`.
4. Задавай **WHAT-вопросы**. Если есть исходники, обязательно предлагай формулировки из них: «Из исходников вижу, что [...]. Верно?».
5. **Ленивое сохранение:** Запиши собранный текст в `current_brief_draft.category` в `project-state.json`, используя шаблон `brief_template`.
6. Переходи к Шагу 3.

### Шаг 3: Ось Z — Аудитория (`stage: audience_who`)
1. Обнови стейт на `audience_who`. **Обязательно прочитай** `parked_knowledge` — скорее всего, пользователь уже что-то рассказывал про аудиторию. Учитывай это, чтобы не спрашивать дважды.
2. Загрузи файл `assets/audiences/{target_audience}.yaml`.
3. Задавай оставшиеся **WHO-вопросы**. Уточни профиль, уровень подготовки и контекст обучения.
4. **Ленивое сохранение:** Запиши текст в `current_brief_draft.audience` в `project-state.json`, используя `brief_template`. Обязательно добавь туда блок с рекомендациями по дизайну (`design_adaptations`).
5. Переходи к Шагу 4.

### Шаг 4: Общие параметры (`stage: general_params`)
1. Обнови стейт на `general_params`. Проверь `parked_knowledge`.
2. Загрузи шаблон [`references/brief-general-template.yaml`](references/brief-general-template.yaml).
3. Задавай общие вопросы (не более 2 за раз): объём курса, редполитика (тон, юмор) и рабочее название.
4. **Ленивое сохранение:** Запиши согласованные параметры в `current_brief_draft.general` в статусе.
5. Переходи к Шагу 5.

### Шаг 5: Сборка Markdown и первичное подтверждение (`stage: final`)
1. Обнови стейт на `final`.
2. Теперь, когда все 4 секции готовы внутри `current_brief_draft`, **создай один физический файл** [workspace/brief.md](../../../workspace/brief.md).
   **ВНИМАНИЕ:** При сборке брифа ОБЯЗАТЕЛЬНО перенеси поля `definition.goal` (Цель) и `definition.measurable_outcome` (Измеримый результат) из загруженных YAML-файлов драйвера и категории в соответствующие разделы. Без этих полей бриф неполный.
3. Запиши всё туда **СТРОГО** по этому шаблону структурирования. Не меняй уровни заголовков:
   ```markdown
   # Бриф проекта

   ## 1. Бизнес-драйвер
   **Цель:** [из definition.goal драйвера]
   **Измеримый результат:** [из definition.measurable_outcome драйвера]
   [текст из current_brief_draft.driver]

   ## 2. Категория курса
   **Цель:** [из definition.goal категории]
   **Измеримый результат:** [из definition.measurable_outcome категории]
   [текст из current_brief_draft.category]

   ## 3. Аудитория
   [текст из current_brief_draft.audience]

   ## 4. Общие параметры
   [текст из current_brief_draft.general]
   ```
4. Покажи пользователю структурированную выжимку из собранного брифа.
5. Спроси подтверждение: **«Бриф собран и сохранен. Всё верно или нужно что-то поправить перед переходом к структуре?»**

### Шаг 6: Цикл правок (`stage: revision`)
1. Если на Шаге 5 пользователь присылает правку или замечание, **НЕ ЗАПУСКАЙ весь скилл заново**. Обнови стейт на `revision` (если это ещё не сделано).
2. Задай уточняющие вопросы по правке, если нужно.
3. Обнови только нужную секцию внутри `current_brief_draft` в памяти (в `project-state.json`).
4. Пересобери и полностью перезапиши файл `workspace/brief.md` с учётом правок.
5. Покажи пользователю **только diff или краткую выжимку того, что изменилось** (например: *"Поправил раздел аудитории. Бриф обновлен."*).
6. Снова попроси подтверждение. Повторяй этот цикл, пока пользователь не скажет, что всё ок.
7. **Выход и завершение:** Когда пользователь дает финальное подтверждение («Да, всё отлично», «Двигаемся дальше»), в `project-state.json` отметь скилл `analysis-general` как `completed`. Обязательно удали ключи `analysis_general_stage`, `parked_knowledge` и `current_brief_draft` из файла json, чтобы очистить кэш статуса. Не переходи на скилл `course-model` без явного согласия пользователя.

> 🛑 **КРИТИЧЕСКОЕ ПРАВИЛО ИНТЕРВЬЮ:**
> НИКОГДА не задавай более 2 вопросов в одном сообщении. Если тебе нужно уточнить 5 деталей, выбери 2 самых важных вопроса сейчас, а остальные задай после ответа. Вываливать вопросы списком **запрещено** — это ломает пайплайн.

> 🛑 **КРИТИЧЕСКОЕ ПРАВИЛО: РАБОТА С ПРОТИВОРЕЧИЯМИ**
> В реальном интервью эксперт часто передумывает или дает несовместимые вводные (например, сначала «курс для всех», а позже «только для руководителей»).
> Если ты видишь, что новая информация противоречит зафиксированной в `current_brief_draft` или `parked_knowledge`:
> 1. **ЗАПРЕЩЕНО** молча перезаписывать данные.
> 2. Явно укажи на противоречие: *"Ранее мы зафиксировали [Версия А], а сейчас вы упоминаете [Версия Б]"*.
> 3. Покажи обе версии и попроси явно подтвердить, какую мы оставляем как финальную.

## Outputs

- Файл [workspace/brief.md](../../../workspace/brief.md) — полностью заполненный бриф (драйвер + категория + аудитория + общие параметры)
- Обновлённый [project-state.json](../../../project-state.json)
- Направление на `course-model` (после подтверждения)
