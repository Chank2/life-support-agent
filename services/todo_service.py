import csv
import uuid
from pathlib import Path
from datetime import date

DATA_DIR = Path("data")
TODO_FILE = DATA_DIR / "todos.csv"

FIELDNAMES = ["id", "date", "title", "priority", "status", "note"]


def ensure_todo_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not TODO_FILE.exists():
        with open(TODO_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_todos():
    ensure_todo_file()

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_todos(todos):
    ensure_todo_file()

    with open(TODO_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(todos)


def add_todo(title: str, todo_date: str, priority: str, note: str = ""):
    todos = load_todos()

    todos.append(
        {
            "id": str(uuid.uuid4()),
            "date": todo_date,
            "title": title,
            "priority": priority,
            "status": "open",
            "note": note,
        }
    )

    save_todos(todos)


def get_today_todos():
    today = date.today().strftime("%Y-%m-%d")
    todos = load_todos()

    return [todo for todo in todos if todo["date"] == today]


def get_open_todos_by_date(todo_date: str):
    todos = load_todos()

    return [
        todo for todo in todos if todo["date"] == todo_date and todo["status"] == "open"
    ]


def complete_todo(todo_id: str):
    todos = load_todos()

    for todo in todos:
        if todo["id"] == todo_id:
            todo["status"] = "done"

    save_todos(todos)


def delete_todo(todo_id: str):
    todos = load_todos()
    todos = [todo for todo in todos if todo["id"] != todo_id]

    save_todos(todos)


def get_todos_text_by_date(todo_date: str):
    todos = get_open_todos_by_date(todo_date)

    if not todos:
        return "今天没有未完成任务。"

    lines = []

    for todo in todos:
        lines.append(
            f"- {todo['title']}｜优先级：{todo['priority']}｜备注：{todo.get('note', '')}"
        )

    return "\n".join(lines)
