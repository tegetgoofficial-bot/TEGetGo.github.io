print(">>> LOADING db_mannager FROM:", __file__)
import sqlite3 as sql
import secrets
import os

# ─── DATABASE PATH ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, ".database", "data_source.db")

# ─── QUERY BUILDER ───────────────────────────────────────────────────────────

class QueryBuilder:
    def __init__(self, table, columns="*"):
        self.table = table
        self.columns = columns
        self.where = None
        self.group_by = None
        self.order_by = None
        self.limit = None

    def set_where(self, clause):
        self.where = clause
        return self

    def set_group_by(self, clause):
        self.group_by = clause
        return self

    def set_order_by(self, clause):
        self.order_by = clause
        return self

    def set_limit(self, n):
        self.limit = n
        return self

    def build(self):
        query = f"SELECT {self.columns} FROM {self.table}"
        if self.where:
            query += f" WHERE {self.where}"
        if self.group_by:
            query += f" GROUP BY {self.group_by}"
        if self.order_by:
            query += f" ORDER BY {self.order_by}"
        if self.limit:
            query += f" LIMIT {self.limit}"
        return query

# ─── ACCOUNT HANDLER ─────────────────────────────────────────────────────────

class accountHandler():
    def __init__(self):
        self.username = None
        self.state = None
        self.isLogin = None
        self.token = secrets.token_hex(32)

    def __str__(self):
        return self.username

    def registerAccount(self, username):
        self.username = username
        return self.token, self


activeAccountTable = {}

# ─── DATABASE FUNCTIONS ───────────────────────────────────────────────────────

def get_list(query):
    print("Executing query:", query)
    con = sql.connect(db_path)
    con.row_factory = sql.Row
    cur = con.cursor()
    try:
        cur.execute(query)
    except Exception as e:
        print("SQL ERROR:", e)
        raise
    data = cur.fetchall()
    con.close()
    return data


