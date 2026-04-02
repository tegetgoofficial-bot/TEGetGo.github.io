print(">>> LOADING db_mannager FROM:", __file__)
# import sqlite3 as sql
from supabase import create_client, Client
import secrets
import os

# ─── DATABASE PATH ────────────────────────────────────────────────────────────

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, ".database", "data_source.db")

# Get these from: Supabase Dashboard > Settings > API
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ─── QUERY BUILDER ───────────────────────────────────────────────────────────

class QueryBuilder:
    def __init__(self, table, columns="*"):
        self.table = table
        self._columns = columns
        self._where = []
        self._joins = []
        self._group_by = None
        self._order_by = None
        self._limit = None

    def __str__(self):
        return self.build(reset=False)

    # --- setters ---
    def set_table(self, new_table):
        self.table = new_table
        return self

    def set_columns(self, columns):
        self._columns = columns or self._columns
        return self

    def join(self, table, clause):
        self._joins.append(f"JOIN {table} ON {clause}")
        return self

    def left_join(self, table, clause):
        self._joins.append(f"LEFT JOIN {table} ON {clause}")
        return self

    def right_join(self, table, clause):
        self._joins.append(f"RIGHT JOIN {table} ON {clause}")
        return self

    def inner_join(self, table, clause):
        self._joins.append(f"INNER JOIN {table} ON {clause}")
        return self

    def add_where(self, clause):
        self._where.append(clause)
        return self

    def set_group_by(self, clause):
        self._group_by = clause
        return self

    def set_order_by(self, clause):
        self._order_by = clause
        return self

    def set_limit(self, n):
        self._limit = n
        return self

    # --- build ---
    def build(self, reset=True):
        query = f"SELECT {self._columns} FROM {self.table}"

        if self._joins:
            query += " " + " ".join(self._joins)
        if self._where:
            query += " WHERE " + " AND ".join(self._where)

        if self._group_by:
            query += f" GROUP BY {self._group_by}"

        if self._order_by:
            query += f" ORDER BY {self._order_by}"

        if self._limit:
            query += f" LIMIT {self._limit}"

        # 2. Reset the 'temporary' filters so the NEXT query starts fresh
        if reset:
            self._where = []    # VERY IMPORTANT: Clears old filters
            self._joins = []    # Clears old joins
            self._group_by = None
            self._order_by = None
            self._limit = None
            # Leave self.table and self._columns alone if you want 
            # this builder to always point to the same table.
        
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
    print("Executing Live Query:", query)
    try:
        # This calls the 'exec_sql' function you will add to Supabase below
        response = supabase.rpc('exec_sql', {'query_text': query}).execute()
        
        # Returns a list of dicts, exactly like your old row_factory
        return response.data if response.data else []
        
    except Exception as e:
        print("LIVE SQL ERROR:", e)
        raise


# ─── TESTING ────────────────────────────────────────────────────────────────
# 1. Initialize your builder for the 'item' table
builder = QueryBuilder("ITEM")
query = builder.set_columns("*").set_limit(5).build()

# 2. Try to fetch the data using your new get_list
try:
    results = get_list(query)
    print(f"--- TEST SUCCESS ---")
    print(f"Found {len(results)} items in Supabase:")
    for row in results:
        print(f"ID: {row['Item_ID']} | Name: {row['name']} | Cost: {row['cost']}")
except Exception as e:
    print(f"--- TEST FAILED ---")
    print(f"Error: {e}")

try:
    # This is equivalent to: SELECT * FROM item WHERE cost > 100 ORDER BY cost DESC LIMIT 5
    res = (
        supabase.table("item")
        .select("*")
        .gt("cost", 100)          # WHERE cost > 100
        .order("cost", desc=True) # ORDER BY cost DESC
        .limit(5)                 # LIMIT 5
        .execute()
    )
    print("SUCCESS:", res.data)

except Exception as e:
    print("FAILED:", e)
