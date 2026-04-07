import sqlite3
import os

DATABASE = 'users.db'

def check_db():
    if not os.path.exists(DATABASE):
        print(f"Error: {DATABASE} does not exist")
        return
        
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Columns in 'users' table:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    conn.close()

if __name__ == '__main__':
    check_db()
