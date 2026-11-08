#!/usr/bin/env python3
"""Офлайн-калькулятор экономики для исследования opus/.

Скрипт не делает сетевых запросов, не читает ключи и не отправляет транзакции.
Значения по умолчанию — наблюдения на 2026-11-08; перед любым решением
подставляйте актуальные цифры из первоисточников (ссылки в 11_istochniki...md).
"""
from __future__ import annotations

import argparse
import math
import sys

ETH_PRICE = 2237.0
UAH_PER_USD = 45.32
STETH_APR = 0.023
LIDO_FEE = 0.10


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def usd(x: float) -> str:
    sign = "-" if x < 0 else ""
    return f"{sign}${abs(x):,.2f}"


def monthly_from_apy(apy: float) -> float:
    return (1 + apy) ** (1 / 12) - 1


def apy_from_apr(apr: float, periods: int) -> float:
    return (1 + apr / periods) ** periods - 1


def apr_from_apy(apy: float, periods: int) -> float:
    return periods * ((1 + apy) ** (1 / periods) - 1)


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(cell.rjust(widths[i]) for i, cell in enumerate(row)))


def cmd_rate(a: argparse.Namespace) -> None:
    if a.apr is not None:
        apy = apy_from_apr(a.apr, a.periods)
        print(f"APR {pct(a.apr)} при {a.periods} начислениях в год -> APY {pct(apy)}")
    else:
        apy = a.apy
        print(f"APY {pct(apy)} -> APR при {a.periods} начислениях в год: {pct(apr_from_apy(apy, a.periods))}")
    m = monthly_from_apy(apy)
    print(f"Месячный эквивалент постоянной эффективной ставки: {pct(m)} (APY/12 = {pct(apy / 12)} — не то же самое)")
    print("Переменные DeFi-ставки не гарантируют такой результат: это иллюстрация постоянной ставки.")


def cmd_capital(a: argparse.Namespace) -> None:
    m = monthly_from_apy(a.apy)
    print(f"Чистая годовая ставка {pct(a.apy)} -> месячный эквивалент {pct(m)}")
    rows = []
    for target in a.monthly:
        cap = target / m if m > 0 else math.inf
        rows.append([usd(target), usd(cap)])
    print_table(["Цель в месяц", "Нужный капитал (линейно)"], rows)
    print("Линейное приближение не учитывает ёмкость пула, проскальзывание, налоги и изменение ставки.")


def cmd_stake(a: argparse.Namespace) -> None:
    net_apr = a.apr * (1 - a.commission)
    real = (1 + net_apr) / (1 + a.inflation) - 1
    print(f"Номинальная ставка {pct(a.apr)}, комиссия оператора {pct(a.commission)} -> чистая {pct(net_apr)} в токенах")
    print(f"Рост доли в предложении при инфляции {pct(a.inflation)}: {pct(real)} (это не доходность в USD)")
    start_usd = a.amount * a.price
    rows = []
    for days in a.days:
        reward = a.amount * net_apr * days / 365
        for dp in a.price_change:
            end_price = a.price * (1 + dp)
            end_usd = (a.amount + reward) * end_price
            rows.append([
                str(days),
                f"{reward:.6f}",
                usd(reward * end_price),
                f"{dp * 100:+.0f}%",
                usd(end_usd - start_usd),
            ])
    print_table(["Дней", "Награда, токенов", "Награда, USD", "Цена токена", "Итог в USD vs старт"], rows)


def csm_bond(n: int, first: float, nxt: float) -> float:
    return 0.0 if n <= 0 else first + nxt * (n - 1)


def csm_operator_eth(n: int, a: argparse.Namespace, per_val: float) -> float:
    if a.ics:
        boosted = min(n, 16)
        return per_val * (a.ics_share * boosted + a.share * (n - boosted))
    return per_val * a.share * n


def cmd_csm(a: argparse.Namespace) -> None:
    gross_apr = a.steth_apr / (1 - a.lido_fee)
    per_val = 32 * gross_apr
    first = a.ics_bond_first if a.ics else a.bond_first
    yearly_costs = a.infra_monthly * 12 + (a.hardware / a.amort_months * 12 if a.amort_months else 0)
    active = max(0.0, 365 - a.activation_days) / 365
    print(f"Валовая ставка валидатора до комиссии Lido: {pct(gross_apr)}; 32 ETH дают {per_val:.4f} ETH/год")
    print(f"Тип оператора: {'ICS' if a.ics else 'permissionless'}; залог первого ключа {first} ETH, следующих {a.bond_next} ETH")
    print(f"Расходы в год: инфраструктура {usd(a.infra_monthly * 12)} + амортизация {usd(yearly_costs - a.infra_monthly * 12)}")
    print(f"Доля первого года после активации: {active:.2f} (ожидание {a.activation_days} дн. в очереди Ethereum)")
    rows = []
    for n in a.validators:
        bond = csm_bond(n, first, a.bond_next)
        rebase = bond * a.steth_apr
        op = csm_operator_eth(n, a, per_val) * active
        total = rebase + op
        total_usd = total * a.eth_price
        incremental = op * a.eth_price - yearly_costs
        rows.append([
            str(n),
            f"{bond:.2f}",
            usd(bond * a.eth_price),
            f"{rebase:.4f}",
            f"{op:.4f}",
            pct(total / bond if bond else 0),
            usd(total_usd - yearly_costs),
            usd(incremental),
        ])
    print_table(
        ["Ключей", "Залог ETH", "Залог USD", "Ребейз ETH/г", "Оператор ETH/г", "Доходность залога",
         "Чистыми USD/г", "Сверх stETH USD/г"],
        rows,
    )
    breakeven = None
    for n in range(1, 501):
        if csm_operator_eth(n, a, per_val) * a.eth_price >= yearly_costs:
            breakeven = n
            break
    if yearly_costs == 0:
        print("Расходы не заданы: точка безубыточности не считается.")
    elif breakeven:
        print(f"Операторская часть покрывает расходы начиная с {breakeven} ключей "
              f"(залог {csm_bond(breakeven, first, a.bond_next):.2f} ETH).")
    else:
        print("Операторская часть не покрывает расходы даже при 500 ключах.")


def cmd_rocketpool(a: argparse.Namespace) -> None:
    active = max(0.0, 365 - a.queue_days - a.activation_days) / 365
    rows = []
    for n in a.validators:
        bond = a.bond * n
        borrowed = (32 - a.bond) * n
        annual = bond * a.validator_apr + borrowed * a.validator_apr * a.commission
        first_year = annual * active
        alt = bond * a.reth_apr
        rows.append([
            str(n),
            f"{bond:.1f}",
            f"{annual:.4f}",
            pct(annual / bond),
            f"{first_year:.4f}",
            f"{alt:.4f}",
            usd((first_year - alt) * a.eth_price - a.infra_monthly * 12),
        ])
    print(f"Доля первого года с наградами: {active:.2f} (очередь RP {a.queue_days} дн. + Ethereum {a.activation_days} дн.)")
    print_table(["Валидаторов", "Залог ETH", "ETH/год (уст.)", "Доходн. залога", "ETH в 1-й год",
                 "rETH на тот же залог", "1-й год vs rETH, USD"], rows)


def cmd_solo(a: argparse.Namespace) -> None:
    for n in a.validators:
        stake = 32 * n
        solo = stake * a.validator_apr
        lst = stake * a.lst_apr
        costs = a.infra_monthly * 12 + (a.hardware / a.amort_months * 12 if a.amort_months else 0)
        diff = (solo - lst) * a.eth_price - costs
        print(f"{n} вал. ({stake} ETH = {usd(stake * a.eth_price)}): соло {solo:.4f} ETH/г, LST {lst:.4f} ETH/г, "
              f"разница {solo - lst:.4f} ETH = {usd((solo - lst) * a.eth_price)}; расходы {usd(costs)}; "
              f"соло лучше LST на {usd(diff)} в год")


def v3_amounts(liquidity: float, p: float, lower: float, upper: float) -> tuple[float, float]:
    sp, sl, su = math.sqrt(p), math.sqrt(lower), math.sqrt(upper)
    if p <= lower:
        return liquidity * (1 / sl - 1 / su), 0.0
    if p >= upper:
        return 0.0, liquidity * (su - sl)
    return liquidity * (1 / sp - 1 / su), liquidity * (sp - sl)


def cmd_lp(a: argparse.Namespace) -> None:
    fees = a.capital * a.fee_apr * a.days / 365 * a.in_range
    rows = []
    for p1 in a.p1:
        if a.full_range:
            r = p1 / a.p0
            lp_rel = 2 * math.sqrt(r) / (1 + r)
            x0, y0 = a.capital / 2 / a.p0, a.capital / 2
            hold = x0 * p1 + y0
            lp = hold * lp_rel
        else:
            x1, y1 = v3_amounts(1.0, a.p0, a.lower, a.upper)
            liquidity = a.capital / (x1 * a.p0 + y1)
            x0, y0 = v3_amounts(liquidity, a.p0, a.lower, a.upper)
            hold = x0 * p1 + y0
            x, y = v3_amounts(liquidity, p1, a.lower, a.upper)
            lp = x * p1 + y
        il = lp / hold - 1
        rows.append([
            f"{p1:,.2f}",
            usd(hold - a.capital),
            usd(lp - a.capital),
            pct(il),
            usd(fees),
            usd(lp + fees - hold),
        ])
    rng = "полный диапазон" if a.full_range else f"диапазон {a.lower:,.0f}–{a.upper:,.0f}"
    print(f"Старт: {usd(a.capital)}, цена {a.p0:,.2f}, {rng}; комиссии {pct(a.fee_apr)} годовых, "
          f"{a.days} дн., доля времени в диапазоне {a.in_range:.0%}")
    print_table(["Цена в конце", "HODL vs старт", "LP vs старт (без комиссий)", "IL vs HODL",
                 "Комиссии", "LP+комиссии vs HODL"], rows)
    print("Газ, ребалансировка и налоги не учтены. Комиссии берутся из допущения, а не из истории пула.")


def cmd_carry(a: argparse.Namespace) -> None:
    margin = a.notional / a.leverage
    capital = a.notional + margin
    funding = a.notional * a.funding_8h * 3 * a.days
    fees = a.notional * (a.spot_fee + a.perp_fee) * (2 if a.exit else 1) + a.transfer_cost
    net = funding - fees
    ann = net / capital * 365 / a.days if a.days else 0
    move_to_liq = 1 / a.leverage - a.mmr
    print(f"Спот {usd(a.notional)} + маржа шорта {usd(margin)} (плечо {a.leverage}x) = капитал {usd(capital)}")
    print(f"Фандинг за {a.days} дн. при {a.funding_8h * 100:.4f}% за 8 ч: {usd(funding)}")
    print(f"Комиссии входа{' и выхода' if a.exit else ''} и переводы: {usd(fees)}")
    print(f"Чистый результат: {usd(net)}; годовых на весь капитал: {pct(ann)}")
    print(f"Шорт ликвидируется примерно при росте цены на {pct(move_to_liq)} (MMR {pct(a.mmr)}), "
          "если не довнести маржу; прибыль по споту на другой бирже автоматически маржу не пополняет.")


def cmd_mining(a: argparse.Namespace) -> None:
    price_kwh = a.tariff_uah / a.uah_per_usd if a.tariff_uah is not None else a.price_kwh
    revenue = a.th * a.hashprice_th * a.hours / 24 * (1 - a.pool_fee)
    kwh = a.power_w / 1000 * a.hours
    cost = kwh * price_kwh
    net = revenue - cost
    print(f"Выручка {usd(revenue)}/сут, электричество {kwh:.1f} кВт·ч x {usd(price_kwh)} = {usd(cost)}/сут")
    print(f"Чистыми до амортизации: {usd(net)}/сут, {usd(net * 30)}/30 дн., {usd(net * 365)}/год")
    if a.hardware:
        if net > 0:
            print(f"Денежная окупаемость {usd(a.hardware)} при неизменном hashprice: {a.hardware / net / 30:.1f} мес.")
        else:
            print("Оборудование не окупается: чистый поток отрицательный.")


def cmd_time(a: argparse.Namespace) -> None:
    rows = []
    for rate in a.rates:
        cost = a.hours * rate
        rows.append([usd(rate), usd(cost), usd(a.net - cost)])
    print(f"Денежный результат {usd(a.net)} за {a.hours} ч")
    print_table(["Стоимость часа", "Стоимость времени", "Результат после времени"], rows)
    if a.hours:
        print(f"Фактическая оплата часа: {usd(a.net / a.hours)}")


def cmd_compare(a: argparse.Namespace) -> None:
    rows = []
    for apy in a.apy:
        m = monthly_from_apy(apy)
        for hourly in a.hourly:
            income = hourly * a.hours_month
            rows.append([pct(apy), usd(hourly), usd(income), usd(income / m)])
    print(f"{a.hours_month} ч работы в месяц против капитала с той же месячной выплатой")
    print_table(["Чистая APY", "Ставка часа", "Доход в месяц", "Эквивалентный капитал"], rows)


def cmd_tax(a: argparse.Namespace) -> None:
    for rate in a.rates:
        print(f"Доход {usd(a.amount)} при ставке {pct(rate)}: налог {usd(a.amount * rate)}, "
              f"остаётся {usd(a.amount * (1 - rate))}")
    print("Ставка и база (вся выручка или прибыль) зависят от режима; см. 07_ukraina_uchet_vyvod.md.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("rate", help="APR <-> APY и месячный эквивалент")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--apr", type=float)
    g.add_argument("--apy", type=float)
    s.add_argument("--periods", type=int, default=365)
    s.set_defaults(func=cmd_rate)

    s = sub.add_parser("capital", help="капитал для целевого месячного дохода")
    s.add_argument("--apy", type=float, required=True)
    s.add_argument("--monthly", type=float, nargs="+", default=[100, 500, 1000])
    s.set_defaults(func=cmd_capital)

    s = sub.add_parser("stake", help="награды стейкинга в токенах и USD")
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--apr", type=float, required=True)
    s.add_argument("--commission", type=float, default=0.0)
    s.add_argument("--inflation", type=float, default=0.0)
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--price-change", type=float, nargs="+", default=[-0.3, 0.0, 0.3])
    s.add_argument("--days", type=int, nargs="+", default=[30, 365])
    s.set_defaults(func=cmd_stake)

    s = sub.add_parser("csm", help="экономика оператора Lido CSM (0x01)")
    s.add_argument("--validators", type=int, nargs="+", default=[1, 5, 10])
    s.add_argument("--ics", action="store_true")
    s.add_argument("--bond-first", type=float, default=2.4)
    s.add_argument("--ics-bond-first", type=float, default=1.5)
    s.add_argument("--bond-next", type=float, default=1.3)
    s.add_argument("--share", type=float, default=0.035)
    s.add_argument("--ics-share", type=float, default=0.06)
    s.add_argument("--steth-apr", type=float, default=STETH_APR)
    s.add_argument("--lido-fee", type=float, default=LIDO_FEE)
    s.add_argument("--eth-price", type=float, default=ETH_PRICE)
    s.add_argument("--infra-monthly", type=float, default=0.0)
    s.add_argument("--hardware", type=float, default=0.0)
    s.add_argument("--amort-months", type=int, default=36)
    s.add_argument("--activation-days", type=int, default=0)
    s.set_defaults(func=cmd_csm)

    s = sub.add_parser("rocketpool", help="экономика мегапула Rocket Pool")
    s.add_argument("--validators", type=int, nargs="+", default=[1, 2, 5])
    s.add_argument("--bond", type=float, default=4.0)
    s.add_argument("--commission", type=float, default=0.05)
    s.add_argument("--validator-apr", type=float, default=STETH_APR / (1 - LIDO_FEE))
    s.add_argument("--reth-apr", type=float, default=0.0193)
    s.add_argument("--queue-days", type=int, default=0)
    s.add_argument("--activation-days", type=int, default=17)
    s.add_argument("--eth-price", type=float, default=ETH_PRICE)
    s.add_argument("--infra-monthly", type=float, default=0.0)
    s.set_defaults(func=cmd_rocketpool)

    s = sub.add_parser("solo", help="соло-валидатор против LST")
    s.add_argument("--validators", type=int, nargs="+", default=[1])
    s.add_argument("--validator-apr", type=float, default=0.026)
    s.add_argument("--lst-apr", type=float, default=STETH_APR)
    s.add_argument("--eth-price", type=float, default=ETH_PRICE)
    s.add_argument("--infra-monthly", type=float, default=0.0)
    s.add_argument("--hardware", type=float, default=0.0)
    s.add_argument("--amort-months", type=int, default=36)
    s.set_defaults(func=cmd_solo)

    s = sub.add_parser("lp", help="LP (Uniswap v3/v2) против удержания тех же активов")
    s.add_argument("--capital", type=float, default=1000.0)
    s.add_argument("--p0", type=float, required=True)
    s.add_argument("--p1", type=float, nargs="+", required=True)
    s.add_argument("--lower", type=float)
    s.add_argument("--upper", type=float)
    s.add_argument("--full-range", action="store_true")
    s.add_argument("--fee-apr", type=float, default=0.0)
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--in-range", type=float, default=1.0)
    s.set_defaults(func=cmd_lp)

    s = sub.add_parser("carry", help="cash-and-carry: спот + шорт перпетуала")
    s.add_argument("--notional", type=float, required=True)
    s.add_argument("--funding-8h", type=float, required=True)
    s.add_argument("--days", type=int, default=30)
    s.add_argument("--leverage", type=float, default=2.0)
    s.add_argument("--spot-fee", type=float, default=0.001)
    s.add_argument("--perp-fee", type=float, default=0.00055)
    s.add_argument("--mmr", type=float, default=0.005)
    s.add_argument("--transfer-cost", type=float, default=0.0)
    s.add_argument("--exit", action="store_true")
    s.set_defaults(func=cmd_carry)

    s = sub.add_parser("mining", help="майнинг: выручка против электричества")
    s.add_argument("--th", type=float, required=True)
    s.add_argument("--power-w", type=float, required=True)
    s.add_argument("--hashprice-th", type=float, default=0.0323)
    s.add_argument("--pool-fee", type=float, default=0.02)
    s.add_argument("--hours", type=float, default=24)
    s.add_argument("--price-kwh", type=float, default=0.0953)
    s.add_argument("--tariff-uah", type=float)
    s.add_argument("--uah-per-usd", type=float, default=UAH_PER_USD)
    s.add_argument("--hardware", type=float, default=0.0)
    s.set_defaults(func=cmd_mining)

    s = sub.add_parser("time", help="результат после стоимости времени")
    s.add_argument("--net", type=float, required=True)
    s.add_argument("--hours", type=float, required=True)
    s.add_argument("--rates", type=float, nargs="+", default=[10, 25, 50])
    s.set_defaults(func=cmd_time)

    s = sub.add_parser("compare", help="навыки против капитала")
    s.add_argument("--hourly", type=float, nargs="+", default=[10, 25, 50])
    s.add_argument("--hours-month", type=float, default=40)
    s.add_argument("--apy", type=float, nargs="+", default=[0.03, 0.05])
    s.set_defaults(func=cmd_compare)

    s = sub.add_parser("tax", help="иллюстрация налоговой нагрузки")
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--rates", type=float, nargs="+", default=[0.23])
    s.set_defaults(func=cmd_tax)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "lp" and not args.full_range and (args.lower is None or args.upper is None):
        print("Для концентрированного диапазона укажите --lower и --upper либо --full-range", file=sys.stderr)
        return 2
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
