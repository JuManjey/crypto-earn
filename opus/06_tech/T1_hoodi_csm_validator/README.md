# T1. Нода Ethereum Hoodi + валидатор Lido CSM (Docker Compose)

Дата проверки версий и параметров: **2026-11-08**.

**Цель.** Бесплатно (на тестовых ETH) пройти полный цикл оператора Lido Community Staking Module на тестнете Hoodi: нода, ключи, залог, депозит, аттестации, мониторинг, обновления, выход. Этот же стек с заменой сети и адресов переносится на mainnet. Экономика mainnet разобрана в [карточке K07](../../03_kartochki/K07_lido_csm_operator.md): при текущих ставках операторская доплата окупает расходы на железо примерно с 6–9 ключей на домашнем оборудовании и с 38–49 ключей на арендованном сервере.

**Что здесь не делается.** Скрипты не создают ключи, не отправляют транзакции, не вносят залог и не подключают кошельки. Эти шаги вы выполняете сами по официальным инструкциям, ссылки приведены ниже.

## 1. Состав

| Компонент | Версия (проверено 2026-11-08) | Источник версии |
|---|---|---|
| Nethermind (EL) | `nethermind/nethermind:2.2.2` | [GitHub Releases](https://github.com/NethermindEth/nethermind/releases), Docker Hub |
| Lighthouse (BN + VC) | `sigp/lighthouse:v8.3.2` | [GitHub Releases](https://github.com/sigp/lighthouse/releases), Docker Hub |
| MEV-Boost | `flashbots/mev-boost:1.12` (тег без `v`) | [GitHub Releases](https://github.com/flashbots/mev-boost/releases), Docker Hub |
| ethstaker-deposit-cli (офлайн, вне Docker) | v1.3.0 | [GitHub Releases](https://github.com/ethstaker/ethstaker-deposit-cli/releases) |

Флаги сверены с документацией: Nethermind [configuration](https://docs.nethermind.io/fundamentals/configuration/) (`--config hoodi`, `--JsonRpc.*`, `--Metrics.*`), Lighthouse book [`bn`](https://lighthouse-book.sigmaprime.io/help_bn.html) и [`vc`](https://lighthouse-book.sigmaprime.io/help_vc.html) (`--network hoodi`, `--builder`, `--builder-proposals`, `--enable-doppelganger-protection`), README MEV-Boost v1.12 (`-hoodi`, `-relays`, `-relay-check`, `-metrics`).

## 2. Требования

| Параметр | Hoodi (обучение) | Mainnet (EIP-7870, роль attester) |
|---|---|---|
| CPU | 4+ ядра | 8 ядер / 16 потоков, PassMark ~3500 ST |
| RAM | 16–32 ГБ | 64 ГБ |
| Диск | 300+ ГБ SSD/NVMe | 4 ТБ NVMe TLC с DRAM; ≥50k IOPS random read, ≥15k random write |
| Сеть | 25+ Мбит/с | 50 Мбит/с вниз / 25 Мбит/с вверх |
| ОС | Ubuntu 24.04/26.04 LTS или Debian 12/13 | то же |
| Время | NTP-синхронизация обязательна | то же |

Источник требований: [EIP-7870](https://eips.ethereum.org/EIPS/eip-7870). Хостинг: Hetzner в своей политике запрещает крипто-нагрузки, включая работу нод, и в 2022 году массово отключал валидаторы Solana ([материал с хронологией](https://orbitservers.io/blog/crypto-friendly-hosting-solana-validators-hetzner-alternative)). Для аренды выбирайте провайдера, который письменно разрешает ноды ([Cherry Servers](https://www.cherryservers.com/ethereum-servers), [OVHcloud](https://www.ovhcloud.com/en/bare-metal/blockchain-server/), [Latitude.sh](https://www.latitude.sh/solutions/ethereum)) и перечитайте их AUP перед заказом.

### Размещение в Украине

| Вариант | Плюсы | Минусы и риски |
|---|---|---|
| Дома | нет абонплаты; электричество около 40–60 Вт × 4.32 грн/кВт·ч ≈ 130–195 грн/мес | отключения света: нужен ИБП или зарядная станция на часы работы ПК и роутера; резервный канал (второй провайдер или мобильный интернет); белый IP или проброс портов; шум и нагрев |
| Аренда bare metal в ЕС | стабильное питание и канал, 10 Гбит/с | $240–280/мес за 4 ТБ/64 ГБ ([Cherry Servers](https://www.cherryservers.com/blog/ethereum-node-cost), 2026); провайдер может отключить за нарушение AUP |
| Облако (AWS/GCP) | быстро и гибко | исходящий трафик и NVMe с нужными IOPS дороги; для постоянной ноды обычно дороже bare metal (точную цену считайте в калькуляторе провайдера) |

CSM допускает кратковременные просадки производительности (performance leeway): валидатор получает операторские награды за период, если эффективность выше порога. Систематически плохая работа даёт «страйки», а при превышении лимита страйков валидатор принудительно выводится со штрафом `badPerformancePenalty` (точные пороги смотрите в параметрах вашего типа оператора). Параметры: [CSM на operator portal](https://operatorportal.lido.fi/modules/community-staking-module).

## 3. Порты

| Порт | Протокол | Наружу? | Назначение |
|---|---|---|---|
| 30303 | TCP+UDP | да (проброс) | P2P Nethermind |
| 9000 | TCP+UDP | да | P2P Lighthouse |
| 9001 | UDP | да | QUIC Lighthouse |
| 8545 | TCP | нет, 127.0.0.1 | JSON-RPC EL (локальная диагностика) |
| 5052 | TCP | нет, 127.0.0.1 | Beacon API |
| 8551, 6060, 5054, 5064, 18550, 18551 | TCP | нет, только внутри Docker-сети | Engine API, метрики, MEV-Boost |

Опубликованные Docker-порты обходят правила ufw (Docker пишет собственные цепочки iptables). Поэтому всё, кроме P2P, привязано к `127.0.0.1` или вообще не публикуется.

## 4. Пошаговый запуск

```bash
cd opus/06_tech/T1_hoodi_csm_validator
cp .env.example .env
$EDITOR .env                       # MEV_RELAYS из allowlist Lido для Hoodi; сверить FEE_RECIPIENT
./scripts/01_prepare_host.sh       # проверки; с --apply-ufw ещё и правила фаервола
./scripts/02_gen_jwt.sh            # secrets/jwt.hex
docker compose pull
docker compose up -d               # execution + consensus + mevboost (без валидатора)
docker compose logs -f --tail=50 consensus
```

Проверка синхронизации:

```bash
# EL: false — синхронизирован
curl -s -X POST -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"eth_syncing","params":[]}' http://127.0.0.1:8545
# CL: "is_syncing":false и "el_offline":false
curl -s http://127.0.0.1:5052/eth/v1/node/syncing
# Готовность: HTTP 200 (206 — ещё синхронизируется)
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5052/eth/v1/node/health
```

После checkpoint sync сверьте финализированный блок с двумя другими провайдерами из [списка эндпоинтов](https://eth-clients.github.io/checkpoint-sync-endpoints/):

```bash
curl -s http://127.0.0.1:5052/eth/v1/beacon/headers/finalized | python3 -m json.tool | grep -E '"slot"|"root"' | head -2
curl -s https://hoodi.beaconstate.ethstaker.cc/eth/v1/beacon/headers/finalized | python3 -m json.tool | grep -E '"slot"|"root"' | head -2
```

### 4.1. Тестовые ETH

Для залога на Hoodi нужен тестовый ETH (2.4 для permissionless-оператора). Берите его только через фаусеты из официальных списков: [hoodi.dev](https://www.hoodi.dev/), документация Lido CSM, каналы EthStaker. Фаусету нужен только адрес. Seed-фразу, приватный ключ или подпись произвольных сообщений не передавайте никогда.

### 4.2. Ключи валидатора (офлайн-машина)

1. Скачайте `ethstaker-deposit-cli` v1.3.0 со [страницы релиза](https://github.com/ethstaker/ethstaker-deposit-cli/releases/tag/v1.3.0) вместе с файлом `.sha256` и сверьте хеш: `sha256sum -c ethstaker_deposit-cli-*-linux-amd64.tar.gz.sha256`.
2. Перенесите архив на машину без сети (live-USB тоже подходит).
3. Сгенерируйте ключи:

```bash
./deposit new-mnemonic \
  --chain hoodi \
  --num_validators 1 \
  --regular_withdrawal \
  --withdrawal_address 0x4473dCDDbf77679A643BdB654dbd86D67F8d32f2
```

   * `--regular_withdrawal` обязателен. Начиная с актуальных версий deposit-cli по умолчанию создаёт компаундинг-валидаторы `0x02`, а 0x01 CSM принимает только `0x01` ([документация deposit-cli](https://deposit-cli.ethstaker.cc/new_mnemonic.html)).
   * Адрес `withdrawal_address` — это Lido Withdrawal Vault для Hoodi с [operator portal](https://operatorportal.lido.fi/modules/community-staking-module) на 2026-11-08. Сверьте его там перед генерацией: изменить withdrawal-адрес после депозита нельзя.
   * Пароль keystore вводите интерактивно. Не передавайте `--keystore_password` в аргументах: он останется в истории shell.
   * Мнемонику запишите на бумагу или сталь. Не фотографируйте, не храните в облаке и не переносите на сервер.
4. **Не делайте депозит через launchpad.** Депозит в 32 ETH делает протокол Lido.
5. На сервер переносите только каталог `validator_keys/` (keystore-*.json и deposit_data-*.json).

### 4.3. Импорт ключей и запуск VC

```bash
./scripts/03_import_keys.sh /path/to/validator_keys
docker compose --profile validator up -d validator
docker compose logs -f --tail=50 validator   # 2–3 эпохи doppelganger protection, затем аттестации
```

### 4.4. Создание оператора в CSM (Hoodi)

1. Откройте [csm.testnet.fi](https://csm.testnet.fi/) (адрес виджета с operator portal), подключите отдельный кошелёк с тестовыми ETH.
2. Загрузите `deposit_data-*.json` и внесите залог (2.4 ETH для первого ключа permissionless-оператора).
3. Виджет проверит подпись, дубликаты и отсутствие предыдущих депозитов. Подписывайте только транзакции, которые показывает виджет, и сверяйте адрес контракта по документации.
4. Дальше ключ ждёт в очереди CSM, потом депозит Lido, потом очередь активации Ethereum. Пока ключ не активирован, держите ноду и VC запущенными: депозит может прийти без предупреждения ([ответ контрибьютора Lido](https://research.lido.fi/t/ido-csm-not-depositing-or-activating-new-nodes-but-allnodes-still-charging-hosting-fees-what-should-i-do/10828)).

Удаление ключа из очереди стоит 0.02 ETH (`keyRemovalCharge`), у ICS 0.01 ETH.

## 5. Мониторинг

Подключите [T2](../T2_monitoring/README.md): он входит во внешнюю сеть `hoodi-csm-net` и снимает метрики Nethermind (`execution:6060`), Lighthouse BN (`consensus:5054`) и VC (`validator:5064`), MEV-Boost (`mevboost:18551`), а также статус ваших валидаторов через Beacon API. Для mainnet держите Prometheus и Alertmanager на отдельном хосте или настройте внешний heartbeat (алерт `Watchdog`): если умрёт сам сервер, локальный мониторинг ничего не отправит.

Готовые дашборды Grafana: [sigp/lighthouse-metrics](https://github.com/sigp/lighthouse-metrics/tree/master/dashboards) (`Summary.json`, `ValidatorClient.json`), [NethermindEth/metrics-infrastructure](https://github.com/NethermindEth/metrics-infrastructure), Node Exporter Full (ID 1860 на grafana.com).

## 6. Обновления

```bash
./scripts/check_client_updates.sh   # 0 — актуально, 10 — есть релизы, 1 — ошибка
```

Порядок: прочитать release notes (обязательные хардфорки, миграции), поменять версию в `.env`, `docker compose pull`, затем перезапуск по одному сервису: `docker compose up -d execution`, дождаться синхронизации, `docker compose up -d consensus`, затем `docker compose --profile validator up -d validator`. На 2026-11-08 апгрейд Glamsterdam (ePBS) работает на Sepolia, его активация на Hoodi отложена, даты для mainnet нет ([блог EF](https://blog.ethereum.org/category/protocol)). Подпишитесь на анонсы: перед хардфорком обновиться обязательно.

## 7. Резервное копирование

| Что | Как | Почему так |
|---|---|---|
| Мнемоника | бумага или сталь, офлайн, в двух местах | восстанавливает ключи; на сервере ей не место |
| Keystore + пароль, slashing protection | `sudo AGE_RECIPIENT=age1... ./scripts/backup_validator_state.sh` | архив шифруется на публичный ключ [age](https://github.com/FiloSottile/age); экспорт EIP-3076 требует остановленного VC, скрипт сам останавливает и запускает его |
| Конфигурация | входит в тот же архив | быстрое восстановление |
| Базы EL/CL | не бэкапить | пересинхронизация с checkpoint sync быстрее и безопаснее |

## 8. Восстановление после сбоя

| Ситуация | Действия |
|---|---|
| EL отстал или база повреждена | `docker compose stop execution`, удалить `data/nethermind`, `docker compose up -d execution` (snap sync) |
| BN не стартует | удалить `data/lighthouse-bn`, перезапустить: checkpoint sync займёт минуты |
| Хост погиб, переезд | **убедитесь, что старый VC не запустится** (сервер выключен или диск стёрт), выждите ≥2 эпохи, восстановите архив, импортируйте slashing protection (`lighthouse --network hoodi account validator slashing-protection import <file>` при остановленном VC), запустите VC с doppelganger protection |
| Отключение света дома | ИБП держит ноду; при долгом отключении нода просто простаивает (штраф за офлайн примерно равен упущенным наградам) |

**Нельзя:** держать «горячий резерв» второго VC с теми же ключами. Два подписывающих экземпляра — прямой путь к double signing и slashing. Ни базы slashing protection, ни doppelganger не защищают от одновременной работы двух экземпляров ([Lighthouse book](https://github.com/sigp/lighthouse/blob/stable/book/src/validator_slashing_protection.md)). Отказоустойчивость без этого риска дают только DVT (Obol/SSV) с порогом подписей.

## 9. Выход

```bash
docker compose run --rm --no-deps -v /path/to/validator_keys:/keys:ro validator \
  lighthouse --network hoodi account validator exit \
  --keystore /keys/<имя-файла-keystore-нужного-валидатора>.json \
  --beacon-node http://consensus:5052
```

Выход возможен через 256 эпох (около 27 часов) после активации и занимает минимум 5 эпох плюс очередь выхода. Затем средства выводятся на withdrawal vault, и залог можно забрать в виджете после закрытия всех штрафов ([Lighthouse: voluntary exit](https://github.com/sigp/lighthouse/blob/stable/book/src/validator_voluntary_exit.md)). Если Lido запросила выход (VEBO), у оператора есть 4 дня, после этого штраф `exitDelayPenalty` и возможный принудительный выход через EIP-7002.

## 10. Переход на mainnet: что меняется

| Параметр | Hoodi | Mainnet (operator portal, 2026-11-08) |
|---|---|---|
| Сеть в compose | `--config=hoodi`, `--network=hoodi`, `-hoodi` | `--config=mainnet`, `--network=mainnet`, `-mainnet` |
| Withdrawal address (keys) | `0x4473dCDDbf77679A643BdB654dbd86D67F8d32f2` | `0xB9D7934878B5FB9610B3fE8A5e441e8fad7E293f` |
| Fee recipient | `0x9b108015fe433F173696Af3Aa0CF7CDb3E104258` | `0x388C818CA8B9251b393131C08a736A67ccB19297` |
| Релеи | allowlist Hoodi | минимум один релей из категории «Mainnet (must use some)» |
| Залог | тестовые ETH | 2.4 ETH за первый ключ (ICS 1.5), 1.3 ETH за следующие |
| Диск | 300+ ГБ | 4 ТБ NVMe |
| Виджет | csm.testnet.fi | csm.lido.fi |

Все адреса перепроверяйте на [operator portal](https://operatorportal.lido.fi/modules/community-staking-module). Если отправить EL-награды не в Lido EL Rewards Vault, это считается кражей: залог штрафуется на сумму плюс фиксированный штраф.

## 11. Безопасность (минимум)

* SSH только по ключам, `PermitRootLogin no`, `unattended-upgrades` для ОС, на сервере ничего лишнего.
* Rewards Address в CSM — холодный кошелёк (аппаратный), Manager Address — отдельный горячий. Lido прямо рекомендует их разделять.
* Админский ноутбук — отдельный пользователь без лишних расширений браузера, аппаратный 2FA. Предварительное расследование взлома Binance 29.10.2026 (около $6.3 млрд) указывает на скомпрометированный ноутбук DevOps-инженера как точку входа ([объявление Binance](https://www.binance.com/en/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7)).
* 1 ноября 2026 года атаковали самохостящиеся BTCPay Server версий ≤2.4.1, хотя исправление вышло ещё в августе ([DefiLlama hacks](https://defillama.com/hacks)). Обновления нужно реально применять.
* Каталог `secrets/` и `.env` не коммитить. Корневой `.gitignore` в `06_tech/` уже это исключает.
