---
name: course-template
description: "Создание YAML-файлов страниц в content/pages/ по иерархии модели (page → scene → frames → blocks) с техническими ID, статусами и production-полями. Используй после course-matrix, когда план содержания утверждён."
---

# Course-Template — Генерация шаблонов страниц

> **Спецификация модели** — [`2_1_course-model`](../2_1_course-model/SKILL.md). Файлы страниц строятся строго по этой модели. YAML-схемы блоков → [`block-types.yaml`](../2_1_course-model/assets/block-types.yaml), типы сцен → [`scene-types.yaml`](../2_1_course-model/assets/scene-types.yaml).

## Inputs

- [project-state.json](../../../project-state.json) (статус проекта)
- [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) (обязательно — должен содержать план содержания: scene → frames → blocks)
- Спецификация модели: [`2_1_course-model/SKILL.md`](../2_1_course-model/SKILL.md), [`assets/block-types.yaml`](../2_1_course-model/assets/block-types.yaml)

## Logic

### Шаг 0: Проверка статуса проекта

Прочитай [project-state.json](../../../project-state.json). Убедись, что скилл `course-matrix` выполнен.

### Шаг 1: Чтение плана и модели

1. Прочитай [workspace/course-structure.yaml](../../../workspace/course-structure.yaml). Определи `structure_type` (`flat` / `modules`). Получи полный список страниц с их планами содержания.
2. Прочитай [`2_1_course-model/assets/block-types.yaml`](../2_1_course-model/assets/block-types.yaml) — YAML-схемы всех типов блоков.

### Шаг 2: Создание файлов страниц

Для каждой страницы из плана создай `.yaml` файл в [content/pages/](../../../content/pages/).

**Именование:** `{порядковый_номер}_{slug}.yaml`
Пример: `01_why-security.yaml`, `02_main-threats.yaml`

На этом этапе план превращается в полноценную структуру по модели: добавляются ID, статусы, поля блоков с плейсхолдерами. Вся метаинформация из плана (purpose, source_ref, content_basis) **переносится в каждый блок**.

Пример файла страницы → [`assets/page-example.yaml`](assets/page-example.yaml)

#### Иерархия файла страницы

```yaml
page:
  id: 1                    # целочисленный PK, сквозная нумерация
  title: "..."
  slug: "..."              # URL-совместимый идентификатор
  goal: "..."              # = learning_objective из плана
  estimated_time: 10       # = duration_minutes из плана
  content_volume: medium   # из плана
  pass_criteria: ...       # опционально, из плана

  scene:
    type: vertical_scene
    id: a1b2c3d            # 7-символьный hex
    frames:
      - id: b2c3d4e
        role: intro
        completion: read
        blocks:
          - id: c3d4e5f
            type: presentation
            block: tinymce
            status: empty
            purpose: "..."
            content_basis: source
            source_ref: "..."
            content: ""
```

#### Правила генерации ID

- **Страницы:** целочисленный Primary Key — `1`, `2`, `3`, ... (сквозная нумерация, независимо от модулей)
- **Сцены, фреймы, блоки, банки вопросов:** 7-символьный hexadecimal — случайная строка из `0-9a-f`. Все ID уникальны в рамках всего курса.

#### Структура блоков

Каждый блок содержит:
- `id` — 7-символьный hex
- `type` — `presentation` или `assessment`
- `block` — конкретный тип блока (из [`block-types.yaml`](../2_1_course-model/assets/block-types.yaml))
- `status` — `empty` (плейсхолдер, контент не заполнен)
- `purpose` — из плана (обязательно)
- `content_basis` — из плана (`source` / `brief` / `generate`)
- `source_ref` — из плана (если есть, иначе не указывать)
- Поля контента — пустые плейсхолдеры по схеме из [`block-types.yaml`](../2_1_course-model/assets/block-types.yaml)

#### Карта заполнения блоков

| Категория | Типы блоков | Заполняет |
|-----------|------------|-----------|
| Presentation | `tinymce`, `quote`, `note`, `table`, `flipcard`, `timeline` | `generation-text` |
| Presentation | `accordion`, `tabs`, `carousel` (структура + вложенные блоки) | `generation-text` |
| Presentation | `image` | `generation-image` |
| Presentation | `hotspot` (фон + точки) | `generation-image` |
| Presentation | `video` | Пользователь вручную |
| Assessment | `single_choice`, `multiple_choice`, `sorting`, `matching`, `sequence`, `classify`, `fill_gap`, `scenario`, `case_question`, `reflection` | `generation-quiz` |

#### Вложенные сцены и банки вопросов

**Вложенная `horizontal_scene`** — помещается в поле `nested_scene` фрейма:

```yaml
- id: e5f6a7b
  role: example
  completion: click_continue
  blocks:
    - id: f6a7b8c
      type: presentation
      block: tinymce
      status: empty
      purpose: "Вводный текст"
      content_basis: brief
      content: ""
  nested_scene:
    type: horizontal_scene
    id: a7b8c9d
    frames:
      - id: b8c9d0e
        role: example
        completion: read
        blocks: [...]
```

**Банк вопросов** — помещается в поле `question_bank` фрейма:

```yaml
- id: c9d0e1f
  role: practice
  completion: pass_assessment
  question_bank:
    type: horizontal_question_bank
    id: d0e1f2a
    frames:
      - id: e1f2a3b
        role: practice
        completion: interact
        blocks:
          - id: f2a3b4c
            type: assessment
            block: single_choice
            status: empty
            purpose: "..."
            content_basis: brief
            question: ""
            options: [...]
            explanation: ""
```

#### Production-поля (добавляются этим скиллом)

| Поле | Уровень | Описание |
|------|---------|----------|
| `status` (`empty` / `filled` / `prompt_ready`) | На каждом блоке | Состояние заполнения |
| `purpose` | На каждом блоке | Из плана — задача блока |
| `source_ref` | На блоках с привязкой к исходникам | Из плана |
| `content_basis` | На каждом блоке | Из плана |
| `content_volume` | На странице | Из плана |

**Общие правила:**
- Генерационные скиллы работают **только с этими файлами** — не обращаются к [course-structure.yaml](../../../workspace/course-structure.yaml)
- Вся метаинформация уже встроена в блоки — generation-скиллы работают автономно
- Каждый тип блока заполняется строго одним скиллом (см. карту выше)

### Шаг 3: Возврат на предыдущий этап (если нужно)

Если пользователь видит проблемы — вернуться к `course-matrix` или `course-structure`. В этом случае **не обновляй** статус в [project-state.json](../../../project-state.json).

### Шаг 4: Обновление [project-state.json](../../../project-state.json) и подтверждение

1. Обнови [project-state.json](../../../project-state.json): отметь `course-template` → `completed`.
2. Сообщи пользователю, сколько файлов страниц создано.
3. Рекомендуй порядок генерации: text → quiz → image.
4. Спроси подтверждение перехода к `generation-text`. Не переходи без согласия.

## Outputs

- Файлы [content/pages/*.yaml](../../../content/pages/) — шаблоны страниц по модели (scene → frames → blocks) с плейсхолдерами и production-полями
- Обновлённый [project-state.json](../../../project-state.json)
- Направление на `generation-text`
