from __future__ import annotations

from budget_app.models import Budget, Transaction


def money(amount: int) -> str:
    return f"{amount}원"


def print_transactions(transactions: list[Transaction]) -> None:
    if not transactions:
        print("표시할 거래가 없습니다.")
        return
    widths = {
        "id": max(10, max(len(tx.id) for tx in transactions)),
        "date": 10,
        "type": 7,
        "category": max(8, max(len(tx.category) for tx in transactions)),
        "amount": max(6, max(len(str(tx.amount)) for tx in transactions)),
    }
    for tx in transactions:
        print(
            f"{tx.id:<{widths['id']}} | {tx.date:<{widths['date']}} | "
            f"{tx.type:<{widths['type']}} | {tx.category:<{widths['category']}} | "
            f"{tx.amount:>{widths['amount']}} | {tx.memo}"
        )


def print_summary(summary: dict[str, object]) -> None:
    if summary["count"] == 0:
        print(f"{summary['month']} 데이터 없음")
        return
    print(f"총 수입: {money(int(summary['income']))}")
    print(f"총 지출: {money(int(summary['expense']))}")
    print(f"잔액: {money(int(summary['balance']))}")
    budget = summary["budget"]
    if isinstance(budget, Budget):
        usage = int(summary["expense"]) / budget.amount * 100
        warning = " [경고: 예산 초과]" if int(summary["expense"]) > budget.amount else ""
        print(f"예산: {money(budget.amount)} (사용률 {usage:.1f}%){warning}")
    print()
    print("지출 TOP")
    for index, (category, amount) in enumerate(summary["top_expenses"], start=1):  # type: ignore[union-attr]
        print(f"{index}. {category} {money(amount)}")
