# Контур оцінювання PayPilot — ДЗ11 / L12

Дата 26.11.2026 · Мандат Ship it · Автор Дмитро Сугак · Кіт 5db4dd0e99a77c3d9ef24f1d6a458cc58ae02293.

## Прогноз перед кроком 1
Див. [незмінний прогноз](protocol/forecast-initial.md). Очікую 6 груп запусків → 1 команду; 0/6 полів попереднього іншого типу звіту → 6/6 нового. Особисту кількість команд не вимірював.

## 1. Інвентаризація

| Точка входу | Тема | Компонент | Вхід | Вихід | Примітка |
|---|---|---|---|---|---|
| loader.load, validate.py | L03 | dataset manager | JSONL | валідовані кейси | старий loader.set_hash хешує байти |
| cli.py, runner.main | L03–L09 | eval runner + storage + reporting | набір/профіль | результати, JSON, консоль | старий змішаний вхід |
| assertions.py | L03–L09 | assertion engine | відповідь/трeйс/очікуване | Verdict | викликає ранер |
| runner.main (запис JSON) | L03–L09 | result storage | результати | reports | старе збереження в runner.main |
| console.py | L03–L09 | reporting | результати | консоль | не запускає модель |
| tools/calibrate_run.py, tools/compare_judges.py | L09–L10 | окремий вхід | розмітка/моделі | калібрування | не daily |
| l08/kit/run_dialog.py (ДЗ07) | L08 | окремий вхід | сценарій | діалог/трейси | у кіті L12 відсутній |
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

## 2. Dataset manager і set_hash

Хешую канонічний JSON сирих вибраних кейсів, sort_keys=True, ensure_ascii=False, separators=(',',':'), ID у відсортованому порядку, рядки через LF; SHA256, перші 12 символів. load_cases фільтрує gate/CASE перед хешуванням. Шість тестів step2: 6/6 PASS.

[Перевірка на тимчасовій копії](reports/hash-verification.json): append змінює хеш; CRLF не змінює; видалення повертає початковий. Tracked sets не змінено. Dry-run l03: 37 кейсів, 37 запланованих викликів агента, 0 судді; unit manual 6, generated 15 — окремо.

## 3. Ранер і assertion engine

collect_oracles збирає engine:disputes з case metadata, перший check_dispute_eligibility з трейсу, відфільтрованого клієнта зі state(customers), спори потрібної транзакції зі state(disputes). assert_case лише читає готовий словник, без HTTP. Step3: 1/1 PASS.

| Шар | Кейси | Заплановано агент | Заплановано суддя |
|---|---:|---:|---:|
| daily | 71 | 72 | 0 |
| all | 90 | 264 | 40 |
| unit L11 | manual 6, generated 15 | — | — |

Dry-run не викликав моделі. Щоденний хеш 58cf5b498718, all ebf346775d7b. Контроль SET=l12 до реалізації кроку5: SKIP, чотири ключі зібрано, exit1, один виклик агента; SKIP-запис видалено за інструкцією, у здачу його не включаю. Його 0.0000 у machine.cost_usd не вважаю доказом безкоштовності — перевіряю облік вартості окремо.

## 4. Запис прогону і два прогони поруч

Перемикаю тільки незмінний промпт через stand.v4.yml; stand.model.yml зберігає gpt-4.1-mini-2025-04-14. Текст після перемикання починається з `(base.v4)`, мітка стенду лишається base.v1.

| Поле | base.v1 | base.v4 |
|---|---|---|
| set | l03 | l03 |
| gate | daily | daily |
| set_hash | 2eeadf91c793 | 2eeadf91c793 |
| prompt_version | base.v1 | base.v4 |
| stand_prompt_label | base.v1 | base.v1 |
| profile | clean | clean |
| judge_model | not-used | not-used |
| rubric_version | rubric.v1 | rubric.v1 |
| elapsed | 144.6 | 88.2 |
| passed | 31 | 32 |
| failed | 6 | 5 |
| machine.cost_usd (тарифна оцінка) | 0.0370704 | 0.0404412 |

Записи: [v1](reports/run-20261125T231236Z.json), [v4](reports/run-20261125T231447Z.json). По37 фактичних звернень чату; це не кількість внутрішніх LLM-викликів. Суддя не використаний; manual6/6 і generated15/15 PASS в обох. Відрізняється одна контрольована умова — текст промпту; elapsed і результати є наслідками, а не умовами.

Шум: еталон курсу1/71 на іншій моделі; власний шум не вимірюю, тому причинний висновок про перевагу v4 не роблю. Перелік змінених ID додам у reporting після кроку6; особисте читання вимірюється окремо.
