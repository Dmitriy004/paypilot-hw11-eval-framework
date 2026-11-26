# PayPilot — ДЗ11 / L12: відтворюваний контур

[Артефакт](eval-framework.md) · [Контракт](protocol/requirements.md) · [Прогноз до прогонів](protocol/forecast-runs.md) · [Умови та джерела](reports/run-environment.json)

Кіт: [5db4dd0e99a77c3d9ef24f1d6a458cc58ae02293](https://github.com/TarasFedorenkoFTV/paypilot-l12-eval/tree/5db4dd0e99a77c3d9ef24f1d6a458cc58ae02293).
Стенд: [paypilot-stand-shared / 74f1995](https://github.com/sergeytkachenko/paypilot-stand-shared/tree/74f1995).
L11: [ДЗ10 resit / c933eae](https://github.com/Dmitriy004/paypilot-hw10-ai-adoption-resit/tree/c933eaecab798152ba1c2e032fd5e8cc8094ffbc). Manual — власний baseline; generated — запасний набір, походження зафіксовано у попередньому ДЗ. Попередні репозиторії не змінюю й тестів сюди не копіюю.

## Запуск

Потрібні Docker Compose >=2.24, локальний стенд з власним OpenAI-ключем та checkout L11. Стандартна розкладка: цей репозиторій, `../paypilot-stand`, `../l11`. Для моєї розкладки змінюються тільки змінні оточення (секретів тут немає):

```powershell
$env:STAND_DIR = '../paypilot-stand-shared'
$env:L11_DIR = '../paypilot-hw10-ai-adoption-resit'
docker compose run --rm eval --dry-run
docker compose run --rm eval
docker compose run --rm --entrypoint pytest eval tests -q
```

Стенд має бути піднятий окремо. `stand.model.yml` фіксує OpenAI `gpt-4.1-mini-2025-04-14` для всіх основних записів, без редагування коду стенду:

```powershell
docker compose -f ../paypilot-stand-shared/docker-compose.yml -f stand.model.yml up -d stand
# Лише підстановка незмінного файлу L11 на кроці4:
docker compose -f ../paypilot-stand-shared/docker-compose.yml -f stand.model.yml -f stand.v4.yml up -d stand
# Повернення на base.v1 із збереженням тієї самої моделі:
docker compose -f ../paypilot-stand-shared/docker-compose.yml -f stand.model.yml up -d stand
```

```powershell
docker compose run --rm -e SET=l03 eval
docker compose run --rm -e SET=l12 eval
docker compose run --rm -e SET=l12 -e DEFECTS=D26 eval
docker compose run --rm eval --compare reports/FILE-V1.json reports/FILE-V4.json
```

Налаштування шляхів і справжній ключ — передумови оточення; між клонуванням і запуском немає редагування коду або встановлення Python вручну. Не запускаю на спільному стенді: контур скидає seed-базу перед кожним кейсом. Коди виходу: 0 — всі перевірки зелені; 1 — FAIL/SKIP/unit failure; 2 — стенд недоступний. На clean червоні кейси не маскую; source sets незмінні.

## Межі доказу

Тарифна оцінка з фактичних токенів — не звірка рахунку провайдера. `machine.requests` зберігає request_id, фактичну модель, токени й джерело ціни; кеш враховано, reasoning уже входить в output. Невідома модель або відсутній usage дає null, а не нуль. [Офіційний тариф](https://developers.openai.com/api/docs/pricing), перевірено26.11.2026.

Час автоматики не називаю особистими хвилинами читання. Еталонний шум1/71 належить моделі курсу, не є моєю оцінкою похибки. Результати одного прогона не доводять production-частоту або перевагу промпту.

Статус: реалізація й вимірювання тривають; до повної здачі потрібні три авторські ADR, фінальні записи та чистий клон.
