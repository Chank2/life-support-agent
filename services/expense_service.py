import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path("data")
EXPENSE_FILE = DATA_DIR / "expenses.csv"

FIELDNAMES = ["date", "item", "amount", "category", "note"]


def ensure_expense_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not EXPENSE_FILE.exists():
        with open(EXPENSE_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def add_expense(
    item: str, amount: int, category: str, expense_date: str, note: str = ""
):

    ensure_expense_file()

    with open(EXPENSE_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

        writer.writerow(
            {
                "date": expense_date,
                "item": item,
                "amount": amount,
                "category": category,
                "note": note,
            }
        )


def load_expenses():
    ensure_expense_file()

    with open(EXPENSE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_today_total():
    today = datetime.now().strftime("%Y-%m-%d")
    expenses = load_expenses()

    total = 0
    for row in expenses:
        if row["date"] == today:
            total += int(row["amount"])

    return total


def get_month_total():
    current_month = datetime.now().strftime("%Y-%m")
    expenses = load_expenses()

    total = 0
    for row in expenses:
        if row["date"].startswith(current_month):
            total += int(row["amount"])

    return total


def get_recent_expenses(limit: int = 10):
    expenses = load_expenses()
    return expenses[-limit:][::-1]


def get_category_summary():
    current_month = datetime.now().strftime("%Y-%m")
    expenses = load_expenses()

    summary = defaultdict(int)

    for row in expenses:
        if row["date"].startswith(current_month):
            summary[row["category"]] += int(row["amount"])

    return dict(summary)


def get_month_expense_report_text():
    current_month = datetime.now().strftime("%Y-%m")
    expenses = load_expenses()

    month_rows = [row for row in expenses if row["date"].startswith(current_month)]

    if not month_rows:
        return "本月还没有消费记录。"

    total = 0
    category_summary = defaultdict(int)
    max_expense = None

    for row in month_rows:
        amount = int(row["amount"])
        total += amount
        category_summary[row["category"]] += amount

        if max_expense is None or amount > int(max_expense["amount"]):
            max_expense = row

    category_lines = []
    for category, amount in sorted(
        category_summary.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = amount / total * 100
        category_lines.append(f"- {category}: {amount:,}日元（{percentage:.1f}%）")

    detail_lines = []
    for row in month_rows:
        detail_lines.append(
            f"- {row['date']}｜{row['item']}｜{int(row['amount']):,}日元｜{row['category']}｜{row.get('note', '')}"
        )

    report = f"""
【本月消费统计摘要】
本月总消费：{total:,}日元
消费笔数：{len(month_rows)}笔

【分类统计】
{chr(10).join(category_lines)}

【最高单笔消费】
{max_expense['date']}｜{max_expense['item']}｜{int(max_expense['amount']):,}日元｜{max_expense['category']}｜{max_expense.get('note', '')}

【本月消费明细】
{chr(10).join(detail_lines)}
"""

    return report.strip()
