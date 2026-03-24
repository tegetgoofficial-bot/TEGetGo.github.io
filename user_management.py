import sqlite3 as sql
import time
import random
import re as _re
from html.entities import html5 as _html5
import html
import secrets
import os

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

class accountHandler():
    def __init__(self):
        self.username = None # Only store what I need, which is username and no password.
        self.state = None # Account state is not used but this suppose to tell if the account even existed. If the app were ever develop further
        self.isLogin = None # This tells me if they logged or not. However, I didn't use it but it can be implimented. If this app was ever develop further
        self.token = secrets.token_hex(32)  # This generate a random text string, in hexadecimal.

    def __str__(self):
        return self.username # This only gives the token which is not useful for an attacker cause it will generate a new one every new login even if it from the same account.

    # This registered the account.
    def registerAccount(self, username):
        self.username = username
        return self.token, self

    
activeAccountTable = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, ".database", "data_source.db")

def get_list(query):
    con = sql.connect(db_path)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return data


def insertUser(username, password, DoB):# I change this part abit, I am pretty sure.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, ".database", "data_source.db")

    con = sql.connect(db_path)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
        (username, password, DoB),
    )
    con.commit()
    con.close()


def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if cur.fetchone() == None:
        con.close()
        return False
    else:
        #cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        cur.execute(f"SELECT * FROM users WHERE username == ? AND password == ?", (username, password))
        # Plain text log of visitor count as requested by Unsecure PWA management
        with open("visitor_log.txt", "r") as file:# I dunno if I should change this part
            number = int(file.read().strip())
            number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))
        # Simulate response time of heavy app for testing purposes
        time.sleep(random.randint(80, 90) / 1000)# I see but like do I need to change this part like showing how I fix this?
        if cur.fetchone() == None:# I also don't know if I should change this part as well
            con.close()
            return False
        else:
            con.close()
            return True

def insertFeedback(feedback):# I do want to make change to this abit but I guess I can built something around it
    feedback = str(feedback)
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO feedback (feedback) VALUES ('{feedback}')")
    con.commit()
    con.close()


def listFeedback():
    # Safely open database connection
    with sql.connect("database_files/database.db") as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM feedback").fetchall()

    # Safely open file for writing
    with open("templates/partials/success_feedback.html", "w", encoding="utf-8") as f:
        for row in data:
            # Escape HTML special characters to prevent breaking the HTML
            safe_content = html.escape(str(row[1]))
            safe_content = safe_content.replace("{", "&#123;").replace("}", "&#125;")# Prevent "{{" trick from XSS exploiting Jinja2
            f.write(f"<p>{safe_content}</p>\n")
        f.flush()

def activeAccount(username, password=None):
    # Check if account is active via token
    if username in activeAccountTable: # Check if it a token or a username
        token = username # If it a token
        return token
    
    # Otherwise, validate credentials
    valid = retrieveUsers(username, password)
    if not valid:
        return False

    # Remove left over token if it existed
    if activeAccountTable.get(username):
        for key, val in list(activeAccountTable.items()):
            if val == username:
                activeAccountTable.pop(key)
                break

    # Create new active account with new token
    newActiveAccount = accountHandler()
    actAccount, regUser = newActiveAccount.registerAccount(username)
    activeAccountTable[actAccount] = regUser
    return actAccount

def deactiveAccount(token=None):
    if token:
        activeAccountTable.pop(token)

def validateWord(wCount=None, word=None):
    # Basic validation
    if wCount is None or word is None:
        return None

    if isinstance(wCount, str) or isinstance(word, int):
        return None

    # Counters
    n = s = U = L = O = Sp = 0

    for letter in word:
        if letter.isdigit():
            n += 1
        elif letter.isalpha():
            s += 1
            if letter.isupper():
                U += 1
            elif letter.islower():
                L += 1
        else:
            if letter != " ":
                O += 1
            else:
                Sp += 1

    # Return structure
    return {
        "validCount": 10 <= wCount <= 20,
        "word": word,
        "numbers": n,
        "spacebar": Sp,
        "letters": s,
        "uppercase": U,
        "lowercase": L,
        "special letters": O
    }
    
def lettersCount(word=None):
    # Return the word count
    if word:
        word = str(word)
        countedWord = 0
        for letter in word:
            if letter == " ":
                continue
            countedWord += 1
        
        return countedWord, word
    return None, word

def validatePass(passWord):
    # Validate word check before return valid
    countedPass, word = lettersCount(passWord)
    validPass = validateWord(countedPass, word)

    # This adds the missing items
    missingItem = {}
    if validPass:
        for category, value in validPass.items():
            if category == "validCount":
                if not validPass["validCount"]:
                    missingItem[category] = value
            elif category == "spacebar":
                if validPass[category]:
                    missingItem[category] = value
            else:
                if not value and category != "spacebar" and category != "validCount":
                    missingItem[category] = value
                    
    elif not validPass:
        return 0, 0 # ERROR Handling
    
    # Return missing item and valid state
    if missingItem:
        return missingItem, False
    else:
        return missingItem, True

# Comment and checks if things works
invalidcheck = validatePass("  ")
validcheck = validatePass("Password_12_9")

print(f"valid check: {validcheck}")
print(f"invalid check: {invalidcheck}")
print("if you can't login cause forgot password then use this account: user: T pass: 1")
