# T3. Офлайн-инструменты: калькулятор экономики и журнал операций

Оба скрипта используют только стандартную библиотеку Python 3.10+, не ходят в сеть, не читают ключи и не отправляют транзакции.

## yield_calc.py — калькулятор

Значения по умолчанию — снимок на 2026-11-08 (ETH $2,237; stETH 2.3%; курс НБУ 45.32 грн/$). Перед решением подставьте актуальные цифры.

| Команда | Что считает | Пример |
|---|---|---|
| `rate` | APR ↔ APY и месячный эквивалент `(1+APY)^(1/12)−1` | `./yield_calc.py rate --apy 0.038` |
| `capital` | капитал для $100/$500/$1000 в месяц (линейно) | `./yield_calc.py capital --apy 0.038` |
| `stake` | награды в токенах и итог в USD при изменении цены | `./yield_calc.py stake --amount 100 --apr 0.0523 --commission 0.05 --inflation 0.0357 --price 89.25` |
| `csm` | экономика оператора Lido CSM 0x01, точка безубыточности | `./yield_calc.py csm --ics --validators 1 5 10 --infra-monthly 8 --hardware 1400 --activation-days 17` |
| `rocketpool` | мегапул Rocket Pool с учётом очереди | `./yield_calc.py rocketpool --queue-days 250` |
| `solo` | соло-валидатор против LST | `./yield_calc.py solo --infra-monthly 260` |
| `lp` | LP Uniswap v3/v2 против удержания тех же активов | `./yield_calc.py lp --p0 2237 --p1 1790 2237 2684 --lower 2013 --upper 2461 --fee-apr 0.25 --in-range 0.6` |
| `carry` | cash-and-carry: спот + шорт перпетуала | `./yield_calc.py carry --notional 5000 --funding-8h 0.0001 --days 90 --exit` |
| `mining` | выручка ASIC против электричества | `./yield_calc.py mining --th 270 --power-w 3645 --tariff-uah 4.32 --hardware 3500` |
| `time` | результат после стоимости времени ($10/$25/$50) | `./yield_calc.py time --net 120 --hours 10` |
| `compare` | навыки против капитала | `./yield_calc.py compare --hours-month 40` |
| `tax` | иллюстрация налоговой нагрузки | `./yield_calc.py tax --amount 1000 --rates 0.23` |

## ledger.py — журнал операций для учёта и налогового консультанта

```bash
./ledger.py init ~/crypto/ledger.csv
./ledger.py add ~/crypto/ledger.csv --date 2026-11-10 --type buy --asset ETH --amount 0.5 \
  --price-usd 2237 --fee-usd 2.24 --platform "Bybit P2P" --source-of-funds "доход ФОП, выписка" \
  --uah-rate 45.32 --document "P2P-ордер 123, банковская выписка"
./ledger.py validate ~/crypto/ledger.csv
./ledger.py report ~/crypto/ledger.csv --year 2026
```

Колонки: `date, type, asset, amount, price_usd, to_asset, to_amount, fee_asset, fee_amount, fee_usd, platform, tx_hash, source_of_funds, uah_rate, document, note`.

Типы операций: `buy` (покупка за фиат), `sell_fiat` (продажа за фиат), `swap` (крипто→крипто, включая стейблкоины), `reward` (стейкинг, airdrop, баунти), `income` (оплата работы в крипте), `transfer` (между своими кошельками), `expense` (расход в фиате, asset=USD).

Отчёт ведёт две книги FIFO:
* **economic** — обмен крипто→крипто считается выбытием по рыночной цене (экономический результат);
* **carryover** — при обмене себестоимость переносится на новый актив. Это ближе к логике законопроекта 10225-д, где обмен ВА на ВА не облагается, но окончательные правила могут отличаться.

Пример: `ledger_example.csv` (все значения помечены как пример). Курс `uah_rate` берите официальный курс НБУ на дату операции. Скрипт его не скачивает, чтобы журнал оставался воспроизводимым.

## Тесты

```bash
python3 tests/test_tools.py    # 12 тестов: FIFO, carryover, комиссии в активе, формулы Uniswap v3, APY
```
