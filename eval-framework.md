# Контур оцінювання PayPilot — ДЗ11 / L12

Дата 26.11.2026 · Мандат Ship it · Автор Дмитро Чернов · Кіт 5db4dd0e99a77c3d9ef24f1d6a458cc58ae02293.

## Прогноз перед кроком 1
Див. [незмінний прогноз](protocol/forecast-initial.md). Очікую 6 груп запусків → 1 команду; 0/6 полів попереднього іншого типу звіту → 6/6 нового. Особисту кількість команд не вимірював.

## 1. Інвентаризація

| Точка входу | Тема | Компонент | Вхід | Вихід | Примітка |
|---|---|---|---|---|---|
| loader.load, validate.py | L03 | dataset manager | JSONL | валідовані кейси | старий loader.set_hash хешує байти |
| cli.py, runner.main | L03–L09 | eval runner + storage + reporting | набір/профіль | результати, JSON, консоль | старий змішаний вхід |
| assertions.py | L03–L09 | assertion engine | відповідь/трeйс/очікуване | Verdict | викликає ранер |
| runner._write_report | L03–L09 | result storage | результати | reports | старе збереження в runner.main |
| console.py | L03–L09 | reporting | результати | консоль | не запускає модель |
| tools/calibrate_judge.py, tools/compare_judges.py | L09–L10 | окремий вхід | розмітка/моделі | калібрування | не daily |
| run_dialog.py (ДЗ07) | L08 | окремий вхід | сценарій | діалог/трейси | у кіті L12 відсутній |
| pytest tests/manual, tests/generated (ДЗ10 resit) | L11 | окремий вхід | функції/движок | pytest exit code | manual власний; generated запасний |
| tools/run_mutants.py (ДЗ10 resit) | L11 | окремий вхід | мутації/тести | виявлені зміни | не включаю в daily |

### П'ять компонентів
| Компонент | Функція | Приймає | Віддає | Чого не знає |
|---|---|---|---|---|
| dataset manager | load_cases, set_hash | імена/фільтри/JSONL | кейси/хеш | HTTP і вердикт агента |
| eval runner | run_case, collect_oracles | кейс/стенд | відповідь/трeйс/словник | правила joint verdict |
| assertion engine | assert_case, joint_checks | готові джерела | рядки/вердикт | HTTP і шляхи файлів |
| result storage | prompt_version, write_record | текст промпту/результати/умови | JSON-запис | бізнес-логіку перевірок |
| reporting | compare | два JSON | відмінності/exit code | виклики стенду |

Стан виконання й результати доповнюю після кожного кроку. Незаповнені розділи не є доказом готовності.
