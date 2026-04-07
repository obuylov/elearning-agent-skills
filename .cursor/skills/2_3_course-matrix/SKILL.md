---
name: course-matrix
description: "Планирование содержания страниц по модели course-model: сцена, фреймы (роли, completion), блоки, вложенные сцены, банки вопросов. Работает в файле course-structure.yaml. Используй после course-structure, когда каркас утверждён."
---

# Course-Matrix — План содержания страниц

> **Спецификация модели** — [`2_1_course-model`](../2_1_course-model/SKILL.md). Обязательно прочитай перед началом работы: иерархия сущностей, типы сцен, роли фреймов, типы блоков и правила вложенности описаны там.

## Inputs

- [project-state.json](../../../project-state.json) (статус проекта)
- [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) (обязательно — каркас от `course-structure`)
- [workspace/brief.md](../../../workspace/brief.md) (бизнес-драйвер, категория, принципы проектирования)
- Файлы [sources/converted/*.md](../../../sources/converted/) (для привязки контента, если есть)
- Спецификация модели: [`2_1_course-model/SKILL.md`](../2_1_course-model/SKILL.md), [`assets/block-types.yaml`](../2_1_course-model/assets/block-types.yaml), [`assets/scene-types.yaml`](../2_1_course-model/assets/scene-types.yaml)

## Logic

### Шаг 0: Проверка статуса проекта

Прочитай [project-state.json](../../../project-state.json). Убедись, что скилл `course-structure` выполнен.

### Шаг 1: Чтение контекста

1. Прочитай [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) — список страниц с целями.
2. Прочитай спецификацию модели ([`2_1_course-model/SKILL.md`](../2_1_course-model/SKILL.md)) — иерархия, роли фреймов, типы блоков, правила вложенности.
3. Прочитай [workspace/brief.md](../../../workspace/brief.md) — бизнес-драйвер, категория, принципы проектирования.
4. Прочитай [project-state.json](../../../project-state.json) → поле `source_mode`.
5. **Если `source_mode: full` или `partial`** — прочитай файлы в [sources/converted/](../../../sources/converted/), составь карту доступного контента.
6. **Если `source_mode: none`** — все блоки будут с `content_basis: generate`.

### Шаг 2: Планирование содержания страниц

Дополни каждую страницу в [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) секцией `scene` — планом сцены с фреймами и блоками. Работай в том же файле, не создавай отдельный.

На этом этапе фокус на **смыслах**: какие фреймы, зачем они, какие блоки, откуда контент. Никаких технических ID — они появятся на этапе `course-template`.

Пример → [`assets/matrix-example.yaml`](assets/matrix-example.yaml)

#### Иерархия плана (по модели)

```
страница
  scene: vertical_scene
    frames:
      - role: intro | concept | example | practice | summary | reflection | transition | reference
        completion: read | open_all_items | watch | pass_assessment | click_continue | interact
        blocks:
          - block: tinymce | image | video | accordion | tabs | carousel | ...
        nested_scene: horizontal_scene (опционально)
        question_bank: vertical_question_bank | horizontal_question_bank (опционально)
```

#### Типы блоков

**Presentation** (подача материала):

| Блок | Назначение | Заполняет |
|------|-----------|-----------|
| `tinymce` | Текст (заголовки, списки, форматирование) | `generation-text` |
| `image` | Изображение / иллюстрация | `generation-image` |
| `video` | Видео-вставка | Пользователь |
| `quote` | Цитата | `generation-text` |
| `note` | Заметка (tip / warning / important / info) | `generation-text` |
| `table` | Таблица | `generation-text` |
| `hotspot` | Интерактивная картинка с точками | `generation-image` |
| `flipcard` | Карточки с переворотом | `generation-text` |
| `timeline` | Временная шкала | `generation-text` |
| `accordion` | Раскрывающиеся секции (внутри: базовые блоки) | `generation-text` |
| `tabs` | Переключаемые вкладки (внутри: базовые блоки) | `generation-text` |
| `carousel` | Перелистываемые карточки (внутри: базовые блоки) | `generation-text` |

**Assessment** (проверка понимания):

| Блок | Назначение | Заполняет |
|------|-----------|-----------|
| `single_choice` | Один правильный ответ | `generation-quiz` |
| `multiple_choice` | Несколько правильных ответов | `generation-quiz` |
| `sorting` | Упорядочивание элементов | `generation-quiz` |
| `matching` | Сопоставление пар | `generation-quiz` |
| `sequence` | Восстановление последовательности | `generation-quiz` |
| `classify` | Классификация по категориям | `generation-quiz` |
| `fill_gap` | Заполнение пропусков | `generation-quiz` |
| `scenario` | Сценарный вопрос с контекстом | `generation-quiz` |
| `case_question` | Вопрос на основе кейса | `generation-quiz` |
| `reflection` | Открытый рефлексивный вопрос | `generation-quiz` |

Подробные YAML-схемы → [`2_1_course-model/assets/block-types.yaml`](../2_1_course-model/assets/block-types.yaml)

#### Роли фреймов

| Роль | Назначение | Рекомендуемый completion | Типичные блоки |
|------|-----------|-------------------------|---------------|
| `intro` | Введение, создание контекста | `read` | `tinymce`, `image`, `video` |
| `concept` | Объяснение, теория | `read`, `open_all_items` | `tinymce`, `accordion`, `tabs`, `image` |
| `example` | Иллюстрация, демонстрация | `read`, `click_continue` | `tinymce`, `image`, `carousel`, nested `horizontal_scene` |
| `practice` | Проверка, упражнение | `pass_assessment`, `interact` | `question_bank`, assessment-блоки |
| `summary` | Итоги, выводы | `read` | `tinymce`, `note`, `quote` |
| `reflection` | Осмысление | `interact` | `reflection`, `tinymce` |
| `transition` | Связка между частями | `read`, `click_continue` | `tinymce` |
| `reference` | Дополнительные материалы | `read` | `tinymce`, `table` |

#### Вложенные сущности

- **`horizontal_scene`** — вкладывается во фрейм. Для пошаговых walkthrough, мини-сценариев. Каждый фрейм внутри — отдельный шаг с собственным completion.
- **`question_bank`** (vertical / horizontal) — вкладывается во фрейм с `role: practice`. Каждый фрейм внутри — один вопрос.

Правила вложенности → [`2_1_course-model/SKILL.md`](../2_1_course-model/SKILL.md), раздел 5.

#### Паттерны по бизнес-драйверам

| Драйвер | Типичная структура | Особенности |
|---------|-------------------|-------------|
| **Compliance** | intro → concept (accordion) → transition → practice (vertical_question_bank) → summary | Банк вопросов обязателен, `pass_criteria: assessment_score` |
| **Rollout** | intro → concept (tabs: было/стало) → example (horizontal_scene: walkthrough) → practice → summary | Горизонтальная сцена для нового процесса |
| **Performance** | intro → concept → example (carousel) → practice (scenario / case_question) → reflection → summary | Сценарные вопросы, reflection |
| **Onboarding** | intro → concept (tabs: по ролям) → example → practice → summary | Tabs для ролевых путей |
| **Knowledge** | intro → concept (accordion: теория) → example (tabs) → practice → summary | Развёрнутая теория, гибкий assessment |

Полные примеры → [`2_1_course-model/assets/examples-by-type.yaml`](../2_1_course-model/assets/examples-by-type.yaml)

#### Поля на этапе матрицы

Для **фреймов:**
- `role` — роль из таблицы выше (обязательно)
- `completion` — условие завершения (обязательно)

Для **блоков:**
- `block` — тип блока (обязательно)
- `purpose` — зачем этот блок, что он должен донести (обязательно, человеческим языком)
- `source_ref` — путь к разделу исходника, формат: `файл#раздел` (если есть)
- `content_basis` — откуда контент: `source` / `brief` / `generate`
- `items_count` — количество элементов для accordion / tabs / carousel / timeline / flipcard / hotspot (если применимо)

Для **банков вопросов:**
- `bank_type` — `vertical_question_bank` или `horizontal_question_bank`
- `questions_count` — количество вопросов

### Шаг 3: Верификация источников контента

> **Критический шаг.** Все вопросы по наличию контента решаются здесь — generation-скиллы не будут обращаться к пользователю за недостающей информацией.

Пройди по всем блокам с `content_basis: source` и проверь:

1. **Существует ли файл** из `source_ref` в [sources/converted/](../../../sources/converted/)?
2. **Есть ли нужный раздел** (после `#` в `source_ref`)?
3. **Достаточно ли контента** для заявленного `purpose` блока?

**Результаты верификации:**

- **Источник найден и достаточен** → оставить `content_basis: source`
- **Источник найден, но недостаточен** → сообщить пользователю
- **Источник не найден** → сообщить пользователю

**Для проблемных блоков** покажи пользователю список с вариантами:
1. **Предоставить информацию** — пользователь даёт факты, данные, текст
2. **Разрешить генерацию** → изменить `content_basis` на `generate`
3. **Указать другой источник** → обновить `source_ref`

**К моменту завершения этого шага все `content_basis: source` блоки должны иметь валидный `source_ref`, а все блоки без покрытия — переведены в `content_basis: generate` или `brief`.**

### Шаг 4: Согласование с пользователем

Покажи план содержания в читаемом виде — постранично. Для каждой страницы покажи:
- Название и цель
- Структуру фреймов (роль → блоки), вложенные сцены и банки вопросов
- Откуда контент (из исходника / генерация)

Дай возможность скорректировать:
- Типы интерактивов и assessment-блоков
- Порядок и роли фреймов
- Назначение блоков
- Типы вложенных сцен и банков вопросов

### Шаг 5: Возврат на предыдущий этап (если нужно)

Если нужно изменить структуру курса или бриф — вернуться к `course-structure` или `analysis-general`. В этом случае **не обновляй** статус в [project-state.json](../../../project-state.json).

### Шаг 6: Обновление [project-state.json](../../../project-state.json) и подтверждение

1. Обнови [project-state.json](../../../project-state.json): отметь `course-matrix` → `completed`.
2. Спроси подтверждение перехода к `course-template`.
3. Не переходи без явного согласия пользователя.

## Outputs

- Файл [workspace/course-structure.yaml](../../../workspace/course-structure.yaml) — дополненный планом содержания (scene → frames → blocks) для каждой страницы
- Обновлённый [project-state.json](../../../project-state.json)
- Направление на `course-template`
