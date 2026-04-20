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

    columns_to_add = [
        ("tag", "TEXT"),
        ("hlr", "TEXT"),
        ("srs", "TEXT"),
        ("tp", "TEXT"),
        ("external_id", "TEXT"),
        ("unique_id", "TEXT")
    ]

    for col_name, col_type in columns_to_add:
        try:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
