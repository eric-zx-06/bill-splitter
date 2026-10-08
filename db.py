import sqlite3

DB_PATH = "bill.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查出来的行能用名字取值，如 r["name"]
    return conn


def init_db():
    # 建三张表：群组、人、支出（v1 只做均摊，所以 expenses 不记分账明细）
    conn = get_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')))"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            name TEXT NOT NULL)"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            paid_by INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')))"""
    )
    # v2 note: custom splits will add expense_splits(expense_id, person_id, share)
    conn.commit()
    conn.close()


def add_group(name):
    conn = get_connection()
    cur = conn.execute("INSERT INTO groups (name) VALUES (?)", (name,))
    conn.commit()
    group_id = cur.lastrowid
    conn.close()
    return group_id


def add_person(group_id, name):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO people (group_id, name) VALUES (?, ?)", (group_id, name)
    )
    conn.commit()
    person_id = cur.lastrowid
    conn.close()
    return person_id


def add_expense(group_id, description, amount, paid_by):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO expenses (group_id, description, amount, paid_by)"
        " VALUES (?, ?, ?, ?)",
        (group_id, description, amount, paid_by),
    )
    conn.commit()
    expense_id = cur.lastrowid
    conn.close()
    return expense_id


def get_groups():
    conn = get_connection()
    rows = conn.execute("SELECT id, name FROM groups ORDER BY id").fetchall()
    conn.close()
    return [(r["id"], r["name"]) for r in rows]


def get_people(group_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name FROM people WHERE group_id = ?", (group_id,)
    ).fetchall()
    conn.close()
    return [(r["id"], r["name"]) for r in rows]


def get_expenses(group_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT e.description, e.amount, p.name AS payer_name
           FROM expenses e JOIN people p ON e.paid_by = p.id
           WHERE e.group_id = ? ORDER BY e.created_at""",
        (group_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_group(group_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE group_id = ?", (group_id,))
    conn.execute("DELETE FROM people WHERE group_id = ?", (group_id,))
    conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()


def delete_person(person_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE paid_by = ?", (person_id,))
    conn.execute("DELETE FROM people WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("db ready")
