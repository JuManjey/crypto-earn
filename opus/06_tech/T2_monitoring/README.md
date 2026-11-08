# T2. Мониторинг ноды и валидаторов (Prometheus + Alertmanager + Grafana)

Дата проверки версий: **2026-11-08**. Этот стек решает две задачи: защищает ваш собственный валидатор (T1) и служит минимальным проверяемым MVP услуги «мониторинг валидаторов для клиентов» ([карточка K03](../../03_kartochki/K03_produkt_monitoring_validatorov.md)).

## Состав и версии

| Сервис | Образ | Назначение |
|---|---|---|
| Prometheus | `prom/prometheus:v3.16.0` | сбор метрик, 23 правила алертов |
| Alertmanager | `prom/alertmanager:v0.34.2` | Telegram + heartbeat (dead man's switch) |
| Grafana | `grafana/grafana:13.3.0` | дашборды |
| node-exporter | `prom/node-exporter:v1.12.1` | диск, память, синхронизация времени |
| blackbox-exporter | `prom/blackbox-exporter:v0.29.1` | готовность beacon API (только HTTP 200) |
| node-health-exporter | сборка из `exporter/` (Python stdlib) | состояние EL/CL и статусы валидаторов через API, только чтение |

## Что проверено

* `promtool check config` и `promtool check rules` (Prometheus 3.16.0): конфиг валиден, 23 правила.
* `promtool test rules tests/rules_test.yml`: алерты на устаревшую голову цепи, падение баланса валидатора, статус slashed и прогноз заполнения диска срабатывают в нужные моменты. Отдельно проверено, что штатный вывод излишка баланса (sweep с 32.05 до 32.00 ETH) не вызывает ложного алерта.
* `amtool check-config` (Alertmanager 0.34.2): конфиг валиден.
* `blackbox_exporter --config.check`: конфиг валиден.
* `python3 tests/test_exporter.py`: 5 тестов экспортера против имитации EL JSON-RPC и Beacon API, включая недоступные эндпоинты.
* `docker compose config`: синтаксис compose валиден.

Повторить проверки можно так (бинарники из официальных релизов Prometheus):

```bash
promtool check config prometheus/prometheus.yml      # путь rule_files внутри контейнера: /etc/prometheus/rules
(cd tests && promtool test rules rules_test.yml)
amtool check-config alertmanager/alertmanager.yml
python3 tests/test_exporter.py
```

## Запуск

Сначала поднимите T1: он создаёт Docker-сеть `hoodi-csm-net`.

```bash
cd opus/06_tech/T2_monitoring
cp .env.example .env
mkdir -p data/prometheus data/alertmanager data/grafana
(umask 077 && mkdir -p secrets)                  # каталог secrets: 700, доступ только у вас
for name in telegram_bot_token telegram_chat_id heartbeat_url; do
  read -rsp "$name: " value && printf '%s' "$value" > "secrets/$name" && echo
done; unset value                                # ввод не отображается и не попадает в историю shell
openssl rand -base64 24 | tr -d '\n' > secrets/grafana_admin_password
chmod 644 secrets/*      # контейнеры читают файлы от своих UID; снаружи их защищает каталог 700
sudo chown -R 65534:65534 data/prometheus data/alertmanager
sudo chown -R 472:472 data/grafana
docker compose up -d --build
```

Секреты вводятся через `read -s`: значения не печатаются на экране, не попадают в `~/.bash_history`, а в файлы записываются без завершающего перевода строки.

Доступ к веб-интерфейсам только через SSH-туннель: `ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 user@host`.

Heartbeat: алерт `Watchdog` срабатывает всегда и уходит каждую минуту на внешний URL (например, проверка типа «dead man's switch» в сервисе уровня Healthchecks.io или аналога). Если сигналы перестали приходить, значит упал сервер, Prometheus или Alertmanager, и внешний сервис уведомит вас сам. Без этого локальный мониторинг молчит именно тогда, когда он нужнее всего.

`VALIDATOR_IDS` в `.env`: индексы или pubkey валидаторов через запятую. Экспортер запрашивает `/eth/v1/beacon/states/head/validators` и отдаёт статус, баланс и признак slashed.

## Алерты

| Группа | Алерты |
|---|---|
| Цепочка | `Watchdog` (heartbeat), `TargetDown` |
| EL | `ExecutionClientDown`, `ExecutionClientSyncing`, `ExecutionHeadStale` (>120 с), `ExecutionLowPeers` |
| CL | `BeaconNodeDown`, `BeaconNodeSyncing`, `BeaconSyncDistance` (>8 слотов), `BeaconOptimistic`, `BeaconSeesExecutionOffline`, `BeaconLowPeers`, `BeaconNotReady` |
| Валидаторы | `ValidatorQueryFailing`, `ValidatorNotActive`, `ValidatorExitingOrSlashed`, `ValidatorSlashed`, `ValidatorBalanceFalling` |
| Хост | `DiskSpaceLow` (<15%), `DiskWillFillIn7Days`, `MemoryLow`, `ClockNotSynchronised`, `ClockOffsetHigh` |

Подавление: если упал EL, не дублируются алерты о его пирах и устаревшей голове; если упал BN, не дублируются алерты о синхронизации и статусах валидаторов.

## Ограничения MVP

* node-exporter работает не в host-сети, поэтому сетевые метрики интерфейсов относятся к контейнеру. Диск, память, CPU и время снимаются корректно через `--path.rootfs=/host`.
* Проверка P2P-портов снаружи (`blackbox-p2p-external`) имеет смысл только с другого хоста. Пример закомментирован в `prometheus.yml`.
* Для клиентов (K03) добавьте отдельный инстанс на клиента или разделение по меткам, а также авторизацию на Grafana (не публикуйте её наружу без reverse proxy с TLS и SSO/паролем).
* Экспортер ограничен 64 валидаторами на инстанс (защита от слишком длинного URL запроса).

## Запуск экспортера без Docker (systemd)

```bash
sudo install -D -m 0755 exporter/node_health_exporter.py /opt/node-health-exporter/node_health_exporter.py
sudo install -m 0644 exporter/node-health-exporter.service /etc/systemd/system/
sudo tee /etc/node-health-exporter.env >/dev/null <<'EOF'
EL_RPC_URL=http://127.0.0.1:8545
CL_API_URL=http://127.0.0.1:5052
VALIDATOR_IDS=
LISTEN_ADDR=127.0.0.1
LISTEN_PORT=9101
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now node-health-exporter
curl -s http://127.0.0.1:9101/metrics | head
```

Юнит запускается с `DynamicUser=yes`, `ProtectSystem=strict` и пустым набором capabilities.
