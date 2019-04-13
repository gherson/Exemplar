import sqlite3

db = sqlite3.connect(':memory:')
global cursor  # So db is available globally.
cursor = db.cursor()
cursor.execute("""CREATE TABLE testing (text_col TEXT NOT NULL, int_col INTEGER)""")
cursor.execute("INSERT INTO testing (text_col) VALUES ('original value')")
cursor.execute("SELECT text_col, int_col FROM testing WHERE 1=2")
row = cursor.fetchone()
print("fetchone(cols) row where false should be None:", row)
cursor.execute("SELECT min(int_col) FROM testing WHERE 1=2")
row = cursor.fetchone()
print("fetchone(min(col)) row where false should be (None,):", row)
cursor.execute("SELECT text_col, int_col FROM testing WHERE 1=2")
rows = cursor.fetchall()
print("fetchall(cols) row where false should be []:", rows)
cursor.execute("SELECT min(int_col) FROM testing WHERE 1=2")
rows = cursor.fetchall()
print("fetchall(min(col)) row where false should be [(None,)]:", rows)