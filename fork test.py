# Adapted from https://code-maven.com/parallel-processing-using-fork-in-python retrieved 3/18/19
# Proves that sqlite3 runs per-process. 3/19/19
import os
import sqlite3
import time

db = sqlite3.connect(':memory:')
global cursor  # So db is available globally.
cursor = db.cursor()
cursor.execute("""CREATE TABLE testing (test_col TEXT NOT NULL)""")
cursor.execute("INSERT INTO testing VALUES ('original value')")

print("Process id before forking: {}".format(os.getpid()))  # Eg, "Process id before forking: 3646"

try:
    pid = os.fork()  # Returns 0 in child only.
except OSError:
    exit("Could not create a child process")

if pid == 0:
    print("In the child process that has the PID {}".format(os.getpid()))  # Eg, "In the child process that has the PID 3647"
    cursor.execute("UPDATE testing SET test_col='new value'")
    cursor.execute("SELECT test_col FROM testing")
    print("Child has updated test_col to:", cursor.fetchone()[0])  # Eg, "new value"
    exit()  # EXIT CHILD EXIT CHILD EXIT CHILD EXIT CHILD

time.sleep(2)  # So above UPDATE has hopefully ran.
cursor.execute("SELECT test_col FROM testing")
print("In the parent, test_col has:", cursor.fetchone()[0])  # Eg, "original value"
print("In the parent process after forking the child {}".format(pid))  # Eg, "In the parent process after forking the child 3647"

# "will wait till the child process ends and then it will return a tuple containing the process ID (PID) of the child
# process and the exit code, the value we passed to exit() in the child process which defaults to 0."
finished = os.waitpid(0, 0)
print(finished)  # Eg, "(3647, 0)"
