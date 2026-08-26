from __future__ import annotations

import csv
import heapq
from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from budget_app.errors import AppError
from budget_app.models import Budget, SearchCriteria, Transaction
from budget_app.repositories import BudgetRepository, CategoryRepository, TransactionRepository
from budget_app.validators import parse_tags, validate_amount, validate_date, validate_month, validate_type


class TransactionService:
    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryRepository,
        budgets: BudgetRepository,
    ) -> None:
        self.transactions = transactions
        self.categories = categories
        self.budgets = budgets

    def create(self, date: str, tx_type: str, category: str, amount: Union[str, int], memo: str, tags: str) -> Transaction:
        transaction = Transaction(
            id=self.transactions.next_id(),
            date=validate_date(date),
            type=validate_type(tx_type),
            category=self.validate_registered_category(category),
            amount=validate_amount(amount),
            memo=memo,
            tags=parse_tags(tags),
        )
        self.transactions.add(transaction)
        return transaction

    def latest(self, limit: int) -> list[Transaction]:
        if limit <= 0:
            raise AppError("--limit은 1 이상이어야 합니다.", "예: --limit 10")
        return heapq.nlargest(limit, self.transactions.stream(), key=lambda item: (item.date, item.id))

    def search(self, criteria: SearchCriteria) -> list[Transaction]:
        if criteria.date_from:
            validate_date(criteria.date_from)
        if criteria.date_to:
            validate_date(criteria.date_to)
        if criteria.tx_type:
            validate_type(criteria.tx_type)
        if criteria.category:
            self.validate_registered_category(criteria.category)
        matched_transactions = [
            transaction
            for transaction in self.transactions.stream()
            if self._matches(transaction, criteria)
        ]
        return sorted(matched_transactions, key=lambda item: (item.date, item.id), reverse=True)

    def update(self, transaction_id: str, changes: dict[str, Optional[str]]) -> bool:
        new_date = validate_date(str(changes["date"])) if changes.get("date") else None
        new_type = validate_type(str(changes["type"])) if changes.get("type") else None
        new_category = self.validate_registered_category(str(changes["category"])) if changes.get("category") else None
        new_amount = validate_amount(str(changes["amount"])) if changes.get("amount") else None

        current_transaction = self.transactions.find_by_id(transaction_id)
        if current_transaction is None:
            return False

        updated_transaction = replace(
            current_transaction,
            date=new_date if new_date is not None else current_transaction.date,
            type=new_type if new_type is not None else current_transaction.type,
            category=new_category if new_category is not None else current_transaction.category,
            amount=new_amount if new_amount is not None else current_transaction.amount,
            memo=str(changes["memo"]) if changes.get("memo") is not None else current_transaction.memo,
            tags=parse_tags(str(changes["tags"])) if changes.get("tags") is not None else current_transaction.tags,
        )
        return self.transactions.update(updated_transaction)

    def delete(self, transaction_id: str) -> bool:
        return self.transactions.delete(transaction_id)

    def summary(self, month: str, top: int) -> dict[str, object]:
        month = validate_month(month)
        if top <= 0:
            raise AppError("--top은 1 이상이어야 합니다.", "예: --top 3")
        total_income = 0
        total_expense = 0
        category_totals: dict[str, int] = {}
        count = 0
        for transaction in self.transactions.stream():
            if not transaction.date.startswith(month):
                continue
            count += 1
            if transaction.type == "income":
                total_income += transaction.amount
            else:
                total_expense += transaction.amount
                category_totals[transaction.category] = category_totals.get(transaction.category, 0) + transaction.amount
        top_expenses = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:top]
        budget = self.budgets.get(month)
        return {
            "month": month,
            "count": count,
            "income": total_income,
            "expense": total_expense,
            "balance": total_income - total_expense,
            "top_expenses": top_expenses,
            "budget": budget,
        }

    def export_csv(
        self,
        out_path: str,
        month: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str],
    ) -> int:
        if month:
            validate_month(month)
        if date_from:
            validate_date(date_from)
        if date_to:
            validate_date(date_to)
        if not month and not (date_from or date_to):
            raise AppError("export는 --month 또는 --from/--to 조건이 필요합니다.", "예: export --out export.csv --month 2024-01")
        criteria = SearchCriteria(date_from=date_from, date_to=date_to)
        matching_transactions = [
            transaction
            for transaction in self.transactions.stream()
            if (not month or transaction.date.startswith(month)) and self._matches(transaction, criteria)
        ]
        with Path(out_path).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "type", "category", "amount", "memo", "tags"])
            writer.writeheader()
            for transaction in sorted(matching_transactions, key=lambda item: (item.date, item.id), reverse=True):
                writer.writerow(
                    {
                        "date": transaction.date,
                        "type": transaction.type,
                        "category": transaction.category,
                        "amount": transaction.amount,
                        "memo": transaction.memo,
                        "tags": ",".join(transaction.tags),
                    }
                )
        return len(matching_transactions)

    def import_csv(self, source_path: str) -> tuple[int, int]:
        imported = 0
        skipped = 0
        with Path(source_path).open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required = {"date", "type", "category", "amount"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise AppError("CSV 헤더가 올바르지 않습니다.", "필수 헤더: date,type,category,amount,memo,tags")
            for row in reader:
                try:
                    self.create(
                        date=row.get("date", ""),
                        tx_type=row.get("type", ""),
                        category=row.get("category", ""),
                        amount=row.get("amount", ""),
                        memo=row.get("memo", ""),
                        tags=row.get("tags", ""),
                    )
                    imported += 1
                except AppError:
                    skipped += 1
        return imported, skipped

    def validate_registered_category(self, category: str) -> str:
        if not self.categories.exists(category):
            raise AppError(f"등록되지 않은 카테고리입니다: {category}", "category list로 확인하거나 category add로 추가하세요.")
        return category

    def _matches(self, transaction: Transaction, criteria: SearchCriteria) -> bool:
        if criteria.date_from and transaction.date < criteria.date_from:
            return False
        if criteria.date_to and transaction.date > criteria.date_to:
            return False
        if criteria.category and transaction.category != criteria.category:
            return False
        if criteria.tx_type and transaction.type != criteria.tx_type:
            return False
        if criteria.query and criteria.query.lower() not in transaction.memo.lower():
            return False
        if criteria.tag and criteria.tag not in transaction.tags:
            return False
        return True


class CategoryService:
    def __init__(self, categories: CategoryRepository, transactions: TransactionRepository) -> None:
        self.categories = categories
        self.transactions = transactions

    def list(self) -> list[str]:
        return self.categories.list()

    def add(self, name: str) -> bool:
        name = name.strip()
        if not name:
            raise AppError("카테고리명은 비워둘 수 없습니다.", "예: category add --name food")
        return self.categories.add(name)

    def remove(self, name: str) -> bool:
        for transaction in self.transactions.stream():
            if transaction.category == name:
                raise AppError(f"사용 중인 카테고리는 삭제할 수 없습니다: {name}", "먼저 해당 거래를 update로 다른 카테고리로 변경하세요.")
        return self.categories.remove(name)


class BudgetService:
    def __init__(self, budgets: BudgetRepository) -> None:
        self.budgets = budgets

    def set(self, month: str, amount: Union[str, int]) -> Budget:
        budget = Budget(month=validate_month(month), amount=validate_amount(amount))
        self.budgets.set(budget)
        return budget
