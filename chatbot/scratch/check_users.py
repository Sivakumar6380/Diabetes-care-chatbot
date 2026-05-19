import sqlite3
import os

db_path = "sql_app.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users;")
        users = cursor.fetchall()
        print(f"Users: {users}")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("Database file not found.")
