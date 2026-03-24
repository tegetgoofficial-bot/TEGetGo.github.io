import sqlite3
import os

def init_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, ".database", "data_source.db")

    # Ensure the .database folder exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Create tables if they don't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS CATEGORIES (
            Category_ID INTEGER PRIMARY KEY,
            Category_Name TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ITEM (
            Item_ID INTEGER PRIMARY KEY,
            Item_Name TEXT NOT NULL,
            Item_AffiliateLink TEXT NOT NULL,
            QuantitySold INTEGER DEFAULT 0,
            Image TEXT NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS ITEM_CATEGORIES (
            Item_ID INTEGER,
            Category_ID INTEGER,
            PRIMARY KEY (Item_ID, Category_ID),
            FOREIGN KEY (Item_ID) REFERENCES ITEM(Item_ID),
            FOREIGN KEY (Category_ID) REFERENCES CATEGORIES(Category_ID)
        )
    ''')

    # Optional: insert sample data if tables are empty
    cur.execute('SELECT COUNT(*) FROM ITEM')
    if cur.fetchone()[0] == 0:
        # Insert some categories
        cur.execute("INSERT INTO CATEGORIES (Category_Name) VALUES ('Bags')")
        cur.execute("INSERT INTO CATEGORIES (Category_Name) VALUES ('Electronics')")

        # Insert some items
        cur.execute("INSERT INTO ITEM (Item_Name, Item_AffiliateLink, QuantitySold, Image) VALUES (?, ?, ?, ?)",
                    ("Crossbody Bag", "https://example.com/crossbody", 1, "image1.jpg"))
        cur.execute("INSERT INTO ITEM (Item_Name, Item_AffiliateLink, QuantitySold, Image) VALUES (?, ?, ?, ?)",
                    ("Smart Bag", "https://example.com/smartbag", 2, "image2.jpg"))

        # Link items to categories
        cur.execute("INSERT INTO ITEM_CATEGORIES (Item_ID, Category_ID) VALUES (1, 1)")
        cur.execute("INSERT INTO ITEM_CATEGORIES (Item_ID, Category_ID) VALUES (2, 1)")

    con.commit()
    con.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()