from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, Optional, Union

from budget_app.errors import AppError
from budget_app.models import Budget, Transaction

DEFAULT_CATEGORIES = ["food", "transport", "rent", "salary", "etc"]


class JsonlStore:
    def __init__(self, data_dir: Union[str, Path]) -> None:
        self.data_dir = Path(data_dir)
        self.transactions_path = self.data_dir / "transactions.jsonl"
        self.categories_path = self.data_dir / "categories.jsonl"
        self.budgets_path = self.data_dir / "budgets.jsonl"

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for path in (self.transactions_path, self.categories_path, self.budgets_path):
            path.touch(exist_ok=True)
        if self.categories_path.stat().st_size == 0:
            with self.categories_path.open("w", encoding="utf-8") as file:
                for name in DEFAULT_CATEGORIES:
                    file.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")

    def iter_json(self, path: Path) -> Iterator[dict[str, Any]]:
        if not path.exists():
            return
        with path.open("r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AppError(
                        f"저장 파일을 읽을 수 없습니다: {path.name}:{line_no}",
                        "파일 내용을 확인하거나 백업에서 복구하세요.",
                    ) from exc
                if isinstance(data, dict):
                    yield data

    def append_json(self, path: Path, data: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(data, ensure_ascii=False) + "\n")

    def rewrite_json(self, path: Path, rows: list[dict[str, Any]]) -> None:
        fd, temp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=self.data_dir)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                for row in rows:
                    file.write(json.dumps(row, ensure_ascii=False) + "\n")
            os.replace(temp_name, path)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise


class TransactionRepository:
    def __init__(self, store: JsonlStore) -> None:
        self.store = store

    def add(self, transaction: Transaction) -> None:
        self.store.append_json(self.store.transactions_path, transaction.to_dict())

    def stream(self) -> Iterator[Transaction]:
        for row in self.store.iter_json(self.store.transactions_path):
            yield Transaction.from_dict(row)

    def next_id(self) -> str:
        max_number = 0
        for transaction in self.stream():
            if transaction.id.startswith("TX-"):
                try:
                    max_number = max(max_number, int(transaction.id[3:]))
                except ValueError:
                    continue
        return f"TX-{max_number + 1:06d}"

    def replace(self, transaction_id: str, updater: Callable[[Transaction], Transaction]) -> bool:
        found = False
        rows: list[dict[str, Any]] = []
        for transaction in self.stream():
            if transaction.id == transaction_id:
                transaction = updater(transaction)
                found = True
            rows.append(transaction.to_dict())
        if found:
            self.store.rewrite_json(self.store.transactions_path, rows)
        return found

    def delete(self, transaction_id: str) -> bool:
        found = False
        rows: list[dict[str, Any]] = []
        for transaction in self.stream():
            if transaction.id == transaction_id:
                found = True
                continue
            rows.append(transaction.to_dict())
        if found:
            self.store.rewrite_json(self.store.transactions_path, rows)
        return found


class CategoryRepository:
    def __init__(self, store: JsonlStore) -> None:
        self.store = store

    def list(self) -> list[str]:
        return sorted(str(row["name"]) for row in self.store.iter_json(self.store.categories_path))

    def exists(self, name: str) -> bool:
        return name in self.list()

    def add(self, name: str) -> bool:
        if self.exists(name):
            return False
        self.store.append_json(self.store.categories_path, {"name": name})
        return True

    def remove(self, name: str) -> bool:
        categories = [category for category in self.list() if category != name]
        if len(categories) == len(self.list()):
            return False
        self.store.rewrite_json(self.store.categories_path, [{"name": category} for category in categories])
        return True


class BudgetRepository:
    def __init__(self, store: JsonlStore) -> None:
        self.store = store

    def set(self, budget: Budget) -> None:
        rows = [row for row in self.store.iter_json(self.store.budgets_path) if row.get("month") != budget.month]
        rows.append(budget.to_dict())
        rows.sort(key=lambda row: str(row["month"]))
        self.store.rewrite_json(self.store.budgets_path, rows)

    def get(self, month: str) -> Optional[Budget]:
        for row in self.store.iter_json(self.store.budgets_path):
            budget = Budget.from_dict(row)
            if budget.month == month:
                return budget
        return None
