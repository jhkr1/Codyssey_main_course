from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from budget_app.decorators import log_timing
from budget_app.errors import AppError
from budget_app.formatters import print_summary, print_transactions
from budget_app.models import SearchCriteria
from budget_app.repositories import BudgetRepository, CategoryRepository, JsonlStore, TransactionRepository
from budget_app.services import BudgetService, CategoryService, TransactionService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m budget_app")
    parser.add_argument("--data-dir", default="./data", help="저장 폴더 경로 (기본: ./data)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("add", help="거래 추가")

    list_parser = subparsers.add_parser("list", help="거래 목록")
    list_parser.add_argument("--limit", type=int, default=10)

    search_parser = subparsers.add_parser("search", help="거래 검색")
    search_parser.add_argument("--from", dest="date_from")
    search_parser.add_argument("--to", dest="date_to")
    search_parser.add_argument("--category")
    search_parser.add_argument("--type", dest="tx_type")
    search_parser.add_argument("--q")
    search_parser.add_argument("--tag")

    summary_parser = subparsers.add_parser("summary", help="월별 요약")
    summary_parser.add_argument("--month", required=True)
    summary_parser.add_argument("--top", type=int, default=3)

    budget_parser = subparsers.add_parser("budget", help="예산 관리")
    budget_sub = budget_parser.add_subparsers(dest="budget_command", required=True)
    budget_set = budget_sub.add_parser("set", help="월 예산 설정")
    budget_set.add_argument("--month", required=True)
    budget_set.add_argument("--amount", required=True)

    category_parser = subparsers.add_parser("category", help="카테고리 관리")
    category_sub = category_parser.add_subparsers(dest="category_command", required=True)
    category_add = category_sub.add_parser("add", help="카테고리 추가")
    category_add.add_argument("--name")
    category_sub.add_parser("list", help="카테고리 목록")
    category_remove = category_sub.add_parser("remove", help="카테고리 삭제")
    category_remove.add_argument("--name", required=True)

    update_parser = subparsers.add_parser("update", help="거래 수정")
    update_parser.add_argument("--id", required=True)
    update_parser.add_argument("--date")
    update_parser.add_argument("--type")
    update_parser.add_argument("--category")
    update_parser.add_argument("--amount")
    update_parser.add_argument("--memo")
    update_parser.add_argument("--tags")

    delete_parser = subparsers.add_parser("delete", help="거래 삭제")
    delete_parser.add_argument("--id", required=True)

    import_parser = subparsers.add_parser("import", help="CSV 가져오기")
    import_parser.add_argument("--from", dest="source", required=True)

    export_parser = subparsers.add_parser("export", help="CSV 내보내기")
    export_parser.add_argument("--out", required=True)
    export_parser.add_argument("--month")
    export_parser.add_argument("--from", dest="date_from")
    export_parser.add_argument("--to", dest="date_to")
    return parser


def build_services(data_dir: str) -> tuple[TransactionService, CategoryService, BudgetService]:
    store = JsonlStore(data_dir)
    store.initialize()
    transactions = TransactionRepository(store)
    categories = CategoryRepository(store)
    budgets = BudgetRepository(store)
    return (
        TransactionService(transactions, categories, budgets),
        CategoryService(categories, transactions),
        BudgetService(budgets),
    )


def prompt(label: str) -> str:
    return input(label).strip()


@log_timing
def run(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(filename="budget_app.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)
    transaction_service, category_service, budget_service = build_services(args.data_dir)

    if args.command == "add":
        transaction = transaction_service.create(
            date=prompt("날짜(YYYY-MM-DD): "),
            tx_type=prompt("타입(income/expense): "),
            category=prompt("카테고리: "),
            amount=prompt("금액(양수): "),
            memo=prompt("메모(선택): "),
            tags=prompt("태그(쉼표로 구분, 없으면 엔터): "),
        )
        print(f"[저장 완료] id={transaction.id}")
    elif args.command == "list":
        print_transactions(transaction_service.latest(args.limit))
    elif args.command == "search":
        print_transactions(
            transaction_service.search(
                SearchCriteria(
                    date_from=args.date_from,
                    date_to=args.date_to,
                    category=args.category,
                    tx_type=args.tx_type,
                    query=args.q,
                    tag=args.tag,
                )
            )
        )
    elif args.command == "summary":
        print_summary(transaction_service.summary(args.month, args.top))
    elif args.command == "budget":
        budget = budget_service.set(args.month, args.amount)
        print(f"[저장 완료] {budget.month} 예산 {budget.amount}원")
    elif args.command == "category":
        if args.category_command == "list":
            for category in category_service.list():
                print(f"- {category}")
        elif args.category_command == "add":
            name = args.name or prompt("카테고리명: ")
            created = category_service.add(name)
            print(f"[저장 완료] category={name}" if created else f"[안내] 이미 존재합니다: {name}")
        elif args.category_command == "remove":
            removed = category_service.remove(args.name)
            print(f"[삭제 완료] category={args.name}" if removed else f"[안내] 없는 카테고리입니다: {args.name}")
    elif args.command == "update":
        changed = transaction_service.update(
            args.id,
            {
                "date": args.date,
                "type": args.type,
                "category": args.category,
                "amount": args.amount,
                "memo": args.memo,
                "tags": args.tags,
            },
        )
        print(f"[수정 완료] id={args.id}" if changed else f"[안내] 없는 거래입니다: {args.id}")
    elif args.command == "delete":
        deleted = transaction_service.delete(args.id)
        print(f"[삭제 완료] id={args.id}" if deleted else f"[안내] 없는 거래입니다: {args.id}")
    elif args.command == "import":
        imported, skipped = transaction_service.import_csv(args.source)
        print(f"[완료] imported={imported}, skipped={skipped}")
    elif args.command == "export":
        count = transaction_service.export_csv(args.out, args.month, args.date_from, args.date_to)
        print(f"[완료] {args.out} ({count} records)")
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except AppError as exc:
        print(f"[오류] {exc.message}", file=sys.stderr)
        if exc.hint:
            print(f"[힌트] {exc.hint}", file=sys.stderr)
        raise SystemExit(1) from None
    except OSError as exc:
        print(f"[오류] 파일 처리 중 문제가 발생했습니다: {exc}", file=sys.stderr)
        print("[힌트] 경로 권한과 파일 존재 여부를 확인하세요.", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
