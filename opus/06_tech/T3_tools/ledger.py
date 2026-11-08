#!/usr/bin/env python3
"""Учёт криптоопераций в CSV с FIFO-себестоимостью (офлайн, без сети и ключей).

Две книги лотов:
  economic  — обмен крипто->крипто считается выбытием по рыночной цене;
  carryover — при обмене себестоимость переносится на полученный актив
              (ближе к логике законопроекта 10225-д, где обмен ВА на ВА
              не облагается; окончательные правила могут отличаться).
Отчёт — материал для налогового консультанта, а не готовая декларация.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

COLUMNS = [
    "date", "type", "asset", "amount", "price_usd", "to_asset", "to_amount",
    "fee_asset", "fee_amount", "fee_usd", "platform", "tx_hash",
    "source_of_funds", "uah_rate", "document", "note",
]
TYPES = {
    "buy": "покупка за фиат",
    "sell_fiat": "продажа за фиат",
    "swap": "обмен крипто->крипто (включая стейблкоины)",
    "reward": "награда: стейкинг, airdrop, баунти",
    "income": "оплата работы в криптовалюте",
    "transfer": "перевод между своими кошельками/аккаунтами",
    "expense": "расход в фиате (сервер, подписка), asset=USD",
}
ONCHAIN_HINT = {"swap", "reward", "income", "transfer"}
EPS = 1e-12


@dataclass
class Lot:
    amount: float
    cost_usd: float


@dataclass
class Book:
    lots: dict[str, deque[Lot]] = field(default_factory=lambda: defaultdict(deque))
    realized: dict[int, float] = field(default_factory=lambda: defaultdict(float))
    warnings: list[str] = field(default_factory=list)

    def add(self, asset: str, amount: float, cost: float) -> None:
        if amount > EPS:
            self.lots[asset].append(Lot(amount, cost))

    def take(self, asset: str, amount: float, where: str) -> float:
        queue = self.lots[asset]
        remaining, cost = amount, 0.0
        while remaining > EPS and queue:
            lot = queue[0]
            used = min(lot.amount, remaining)
            part = lot.cost_usd * used / lot.amount
            cost += part
            lot.amount -= used
            lot.cost_usd -= part
            remaining -= used
            if lot.amount <= EPS:
                queue.popleft()
        if remaining > 1e-9:
            self.warnings.append(f"{where}: выбытие {amount} {asset} больше остатка на {remaining:.8f}")
        return cost

    def holdings(self) -> dict[str, tuple[float, float]]:
        out = {}
        for asset, queue in self.lots.items():
            amt = sum(l.amount for l in queue)
            if amt > EPS:
                out[asset] = (amt, sum(l.cost_usd for l in queue))
        return out


def fnum(value: str, name: str, row_no: int, required: bool = False) -> float:
    value = (value or "").strip()
    if not value:
        if required:
            raise ValueError(f"строка {row_no}: поле {name} обязательно")
        return 0.0
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"строка {row_no}: {name}={value!r} не число") from exc


def parse_date(value: str, row_no: int) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"строка {row_no}: дата {value!r} не в формате ISO (YYYY-MM-DD[THH:MM[:SS]])")


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"в файле нет колонок: {', '.join(missing)}")
        rows = []
        for i, row in enumerate(reader, start=2):
            row["_row"] = i
            row["_dt"] = parse_date(row["date"], i)
            rows.append(row)
    rows.sort(key=lambda r: (r["_dt"], r["_row"]))
    return rows


def validate_row(row: dict) -> list[str]:
    n = row["_row"]
    problems = []
    t = row["type"].strip()
    if t not in TYPES:
        problems.append(f"строка {n}: неизвестный type={t!r}; допустимо: {', '.join(TYPES)}")
        return problems
    amount = fnum(row["amount"], "amount", n, required=True)
    if amount <= 0:
        problems.append(f"строка {n}: amount должен быть > 0")
    if t in {"buy", "sell_fiat", "swap", "reward", "income"} and fnum(row["price_usd"], "price_usd", n) <= 0:
        problems.append(f"строка {n}: для {t} нужна price_usd > 0 (рыночная цена единицы актива)")
    if t == "swap" and (not row["to_asset"].strip() or fnum(row["to_amount"], "to_amount", n) <= 0):
        problems.append(f"строка {n}: для swap нужны to_asset и to_amount")
    if row["fee_asset"].strip() and fnum(row["fee_amount"], "fee_amount", n) <= 0:
        problems.append(f"строка {n}: указан fee_asset без fee_amount")
    if t in ONCHAIN_HINT and not row["tx_hash"].strip() and not row["platform"].strip():
        problems.append(f"строка {n}: нет ни tx_hash, ни platform — операцию будет трудно подтвердить")
    if t in {"buy", "income"} and not row["source_of_funds"].strip():
        problems.append(f"строка {n}: не указано происхождение средств (source_of_funds)")
    if t != "transfer" and not row["uah_rate"].strip():
        problems.append(f"строка {n}: нет курса НБУ (uah_rate) на дату операции")
    return problems


def process(rows: list[dict], reward_basis: str) -> dict:
    eco, carry = Book(), Book()
    fiat_proceeds = defaultdict(float)
    rewards_usd = defaultdict(float)
    rewards_uah = defaultdict(float)
    fees_usd = defaultdict(float)
    expenses_usd = defaultdict(float)
    for row in rows:
        n, year, t = row["_row"], row["_dt"].year, row["type"].strip()
        asset = row["asset"].strip().upper()
        amount = fnum(row["amount"], "amount", n)
        price = fnum(row["price_usd"], "price_usd", n)
        fee_usd = fnum(row["fee_usd"], "fee_usd", n)
        fee_asset = row["fee_asset"].strip().upper()
        fee_amount = fnum(row["fee_amount"], "fee_amount", n)
        uah = fnum(row["uah_rate"], "uah_rate", n)
        where = f"строка {n}"
        fiat_fee = fee_usd if not fee_asset else 0.0
        fees_usd[year] += fee_usd

        if t == "buy":
            cost = amount * price + fiat_fee
            eco.add(asset, amount, cost)
            carry.add(asset, amount, cost)
        elif t == "sell_fiat":
            proceeds = amount * price - fiat_fee
            eco.realized[year] += proceeds - eco.take(asset, amount, where)
            carry.realized[year] += proceeds - carry.take(asset, amount, where)
            fiat_proceeds[year] += proceeds
        elif t == "swap":
            to_asset = row["to_asset"].strip().upper()
            to_amount = fnum(row["to_amount"], "to_amount", n)
            value = amount * price - fiat_fee
            eco.realized[year] += value - eco.take(asset, amount, where)
            eco.add(to_asset, to_amount, value)
            carried = carry.take(asset, amount, where)
            carry.add(to_asset, to_amount, carried + fiat_fee)
        elif t in {"reward", "income"}:
            fmv = amount * price
            eco.add(asset, amount, fmv)
            carry.add(asset, amount, fmv if reward_basis == "fmv" else 0.0)
            rewards_usd[year] += fmv
            rewards_uah[year] += fmv * uah
        elif t == "expense":
            expenses_usd[year] += amount
        if fee_asset and fee_amount > 0:
            eco.realized[year] -= eco.take(fee_asset, fee_amount, where + " (комиссия)")
            carry.realized[year] -= carry.take(fee_asset, fee_amount, where + " (комиссия)")
    return {
        "eco": eco, "carry": carry, "fiat_proceeds": fiat_proceeds, "rewards_usd": rewards_usd,
        "rewards_uah": rewards_uah, "fees_usd": fees_usd, "expenses_usd": expenses_usd,
    }


def cmd_init(a: argparse.Namespace) -> int:
    path = Path(a.file)
    if path.exists():
        print(f"{path} уже существует — не перезаписываю", file=sys.stderr)
        return 1
    with path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(COLUMNS)
    print(f"Создан {path}. Типы операций: " + "; ".join(f"{k} — {v}" for k, v in TYPES.items()))
    return 0


def cmd_add(a: argparse.Namespace) -> int:
    path = Path(a.file)
    if not path.exists():
        print(f"{path} не найден, сначала выполните init", file=sys.stderr)
        return 1
    row = {c: "" for c in COLUMNS}
    for c in COLUMNS:
        value = getattr(a, c, None)
        if value is not None:
            row[c] = str(value)
    row["_row"] = "новая"
    try:
        row["_dt"] = parse_date(row["date"], 0)
        problems = validate_row(row)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    hard = [p for p in problems if "нужн" in p or "неизвестный" in p or "> 0" in p]
    for p in problems:
        print(("ОШИБКА: " if p in hard else "Предупреждение: ") + p, file=sys.stderr)
    if hard:
        return 1
    with path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([row[c] for c in COLUMNS])
    print("Запись добавлена.")
    return 0


def cmd_validate(a: argparse.Namespace) -> int:
    try:
        rows = read_rows(Path(a.file))
        problems = [p for r in rows for p in validate_row(r)]
    except ValueError as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        return 1
    for p in problems:
        print(p)
    print(f"Проверено строк: {len(rows)}, замечаний: {len(problems)}")
    return 0 if not problems else 3


def cmd_report(a: argparse.Namespace) -> int:
    try:
        rows = read_rows(Path(a.file))
    except ValueError as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        return 1
    if a.year:
        rows_for_calc = [r for r in rows if r["_dt"].year <= a.year]
    else:
        rows_for_calc = rows
    res = process(rows_for_calc, a.reward_basis)
    years = sorted({r["_dt"].year for r in rows_for_calc})
    if a.year:
        years = [a.year]
    print(f"Файл: {a.file}; операций учтено: {len(rows_for_calc)}; база наград в carryover: {a.reward_basis}")
    print("\nПо годам (USD; UAH — по курсам из колонки uah_rate):")
    print("Год  | Реализ. economic | Реализ. carryover | Выручка в фиат | Награды/оплата USD | Награды UAH | Комиссии | Расходы")
    for y in years:
        print(f"{y} | {res['eco'].realized[y]:16.2f} | {res['carry'].realized[y]:17.2f} | "
              f"{res['fiat_proceeds'][y]:14.2f} | {res['rewards_usd'][y]:18.2f} | {res['rewards_uah'][y]:11.2f} | "
              f"{res['fees_usd'][y]:8.2f} | {res['expenses_usd'][y]:7.2f}")
    print("\nОстатки (economic FIFO):")
    for asset, (amt, cost) in sorted(res["eco"].holdings().items()):
        print(f"  {asset:8s} {amt:.8f}  себестоимость {cost:.2f} USD  средняя {cost / amt:.4f}")
    print("\nОстатки (carryover FIFO):")
    for asset, (amt, cost) in sorted(res["carry"].holdings().items()):
        print(f"  {asset:8s} {amt:.8f}  себестоимость {cost:.2f} USD")
    warnings = res["eco"].warnings
    if warnings:
        print("\nПредупреждения:")
        for w in warnings:
            print("  " + w)
    print("\nЭто расчётная справка для консультанта: момент и база налога определяются правилами, "
          "действующими на дату операции.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init", help="создать пустой журнал")
    s.add_argument("file")
    s.set_defaults(func=cmd_init)
    s = sub.add_parser("add", help="добавить операцию")
    s.add_argument("file")
    for c in COLUMNS:
        s.add_argument("--" + c.replace("_", "-"), dest=c, required=c in {"date", "type", "asset", "amount"})
    s.set_defaults(func=cmd_add)
    s = sub.add_parser("validate", help="проверить журнал")
    s.add_argument("file")
    s.set_defaults(func=cmd_validate)
    s = sub.add_parser("report", help="FIFO-отчёт по годам")
    s.add_argument("file")
    s.add_argument("--year", type=int)
    s.add_argument("--reward-basis", choices=["fmv", "zero"], default="fmv")
    s.set_defaults(func=cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
