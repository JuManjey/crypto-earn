# 06. Технические инструкции

| Каталог | Что внутри | Статус проверки |
|---|---|---|
| [T1_hoodi_csm_validator](T1_hoodi_csm_validator/README.md) | Nethermind + Lighthouse + MEV-Boost для Lido CSM на Hoodi, скрипты подготовки хоста, JWT, импорта ключей, бэкапа, сверки версий; путь на mainnet | `docker compose config`, `bash -n`, shellcheck (style) без замечаний; сверка версий проверена на живом GitHub API |
| [T2_monitoring](T2_monitoring/README.md) | Prometheus, 23 алерта, Alertmanager (Telegram + heartbeat), Grafana, node/blackbox exporters, собственный экспортер статусов EL/CL/валидаторов | promtool (config, rules, unit-тесты алертов), amtool, blackbox `--config.check`, 5 тестов экспортера |
| [T3_tools](T3_tools/README.md) | `yield_calc.py` (все расчёты исследования), `ledger.py` (учёт операций с FIFO для налогового консультанта) | 12 модульных тестов |

Общие правила для всего каталога:

* Ничего не подключается к кошелькам, не отправляет транзакций и не тратит деньги. Шаги с деньгами (залог, депозит, покупка) выполняются вручную по официальным инструкциям.
* Секреты (`secrets/`, `.env`, `validator_keys/`) исключены через [.gitignore](.gitignore). Пароли вводятся интерактивно, а не в аргументах команд.
* Seed-фраза никогда не попадает на сервер. Ключи генерируются на офлайн-машине.
* Версии зафиксированы на 2026-11-08 и проверены по GitHub Releases и Docker Hub; перед запуском прогоните `T1_hoodi_csm_validator/scripts/check_client_updates.sh`.
