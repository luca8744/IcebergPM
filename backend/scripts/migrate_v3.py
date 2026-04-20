import sqlite3
import os

# Determinazione del percorso del database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(BASE_DIR, "iceberg_pm.db")

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print(f"Migrating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Aggiungi colonna is_private a items
        print("Adding column 'is_private' to 'items' table...")
        cursor.execute("ALTER TABLE items ADD COLUMN is_private BOOLEAN DEFAULT 0")
        print("Added column 'is_private' to 'items' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'is_private' already exists.")
        else:
            print(f"Error adding column: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
