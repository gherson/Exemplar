import sqlite3

""" Last test added 2019-04-27
In sum, 
* fetchone() always returns a tuple unless 0 rows (in which case None is returned).
* fetchall() always returns a list, empty if 0 rows and no aggregate function in the select clause, and of 
tuple/s otherwise.
"""

db = sqlite3.connect(':memory:', isolation_level=None)
cursor = db.cursor()

cursor.execute("CREATE TABLE testing (text_col TEXT NOT NULL, int_col INTEGER)")
cursor.execute("INSERT INTO testing (text_col, int_col) VALUES ('original value', NULL)")
cursor.execute("SELECT int_col FROM testing")
row = cursor.fetchone()
print("fetchone(col) row of NULL value is (None,):", row)

cursor.execute("SELECT int_col FROM testing")
row = cursor.fetchall()
print("fetchall(col) row of NULL value is [(None,)]:", row)

cursor.execute("SELECT text_col, int_col FROM testing WHERE 1=2")
row = cursor.fetchone()
print("fetchone(cols) row where false is None:", row)

cursor.execute("SELECT min(int_col) FROM testing WHERE 1=2")
row = cursor.fetchone()
print("fetchone(min(col)) row where false is (None,):", row)

cursor.execute("SELECT min(int_col), max(int_col) FROM testing WHERE 1=2")
row = cursor.fetchone()
print("fetchone(min(col), max(col)) row where false is (None, None):", row)

cursor.execute("SELECT text_col, int_col FROM testing WHERE 1=2")
rows = cursor.fetchall()
print("fetchall(cols) row where false is []:", rows)

cursor.execute("SELECT min(int_col) FROM testing WHERE 1=2")
rows = cursor.fetchall()
print("fetchall(min(col)) row where false is [(None,)]:", rows)

cursor.execute("BEGIN")  # Turns off auto-commit.
cursor.execute("INSERT INTO testing (text_col) VALUES ('value 2')")
cursor.execute("SELECT text_col, int_col FROM testing")
rows = cursor.fetchall()
print("2nd, uncommitted insertion is selectable within this thread only:", rows)