import sqlite3
import os

# Determinazione del percorso del database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(BASE_DIR, "iceberg_pm.db")

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Adding column reference_client to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN reference_client TEXT")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column reference_client already exists.")
        else:
            print(f"Error adding reference_client: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
