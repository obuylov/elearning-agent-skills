Конвертируй исходные файлы из `sources/original/` в Markdown.

## Действие

Запусти Python-скрипт конвертации:

```bash
python3 .cursor/skills/1_1_analysis-scanner/scripts/convert.py
```

Если нужно переконвертировать все файлы заново (включая уже существующие), добавь флаг `--force`:

```bash
python3 .cursor/skills/1_1_analysis-scanner/scripts/convert.py --force
```

## После конвертации

Покажи пользователю результат (сколько файлов сконвертировано, пропущено, ошибок). Если ошибок нет — предложи запустить `analysis-scanner` для анализа и классификации сконвертированных материалов.
