import sqlite3

db = sqlite3.connect(':memory:', isolation_level=None)
cursor = db.cursor()

cursor.execute("CREATE TABLE testing (text_col TEXT NOT NULL, int_col INTEGER)")
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

# Uncommitted insertions are selectable (within this thread only).
cursor.execute("BEGIN")  # Turns off auto-commit.
cursor.execute("INSERT INTO testing (text_col) VALUES ('value 2')")
cursor.execute("SELECT text_col, int_col FROM testing")
rows = cursor.fetchall()
print("rows:", rows)