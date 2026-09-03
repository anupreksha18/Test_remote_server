from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("ExpenseTracker")


def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                amount NOT NULL,
                note TEXT DEFAULT ''
            )
        """)


init_db()


@mcp.tool
def add_expense(
    date: str,
    category: str,
    subcategory: str = '',
    amount: float = 0.0
) -> dict:
    """Add an expense to the database."""

    with sqlite3.connect(DB_PATH) as c:
        cursor = c.execute(
            """
            INSERT INTO expenses (date, category, subcategory, amount)
            VALUES (?, ?, ?, ?)
            """,
            (date, category, subcategory, amount)
        )

        expense_id = cursor.lastrowid

    return {
        "status": "ok",
        "id": expense_id
    }


@mcp.tool
def list_expenses(start_date,end_date):
    """List all expenses."""

    with sqlite3.connect(DB_PATH) as c:
        curr = c.execute("""
            SELECT id, date, category, subcategory, amount, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        """,(start_date,end_date))

        cols = [d[0] for d in curr.description]

        return [dict(zip(cols, row)) for row in curr.fetchall()]

@mcp.tool
def summarize(start_date,end_date,category=None):
    '''Summarize expenses by category and subcategory within a date range.'''
    with sqlite3.connect(DB_PATH) as c:
        query=(
            """SELECT category,SUM(amount) as total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """
        )
        params=[start_date,end_date]

        if category:
            query+=" AND category=?"
            params.append(category)

        query+=" GROUP BY category ORDER BY category ASC"

        curr=c.execute(query,params)
        cols=[d[0] for d in curr.description]
        return [dict(zip(cols,row)) for row in curr.fetchall()]


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)