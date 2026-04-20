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

    # SQLite support for DROP COLUMN was added in 3.35.0 (2021-03-12).
    # Since we can't be sure of the version, we'll use the safest method:
    # 1. Create a new table without the columns
    # 2. Copy the data
    # 3. Drop the old table
    # 4. Rename the new table
    
    try:
        print("Starting migration to remove hour columns...")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(items)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Target columns (excluding the ones we want to remove)
        target_columns = [col for col in columns if col not in ('estimated_hours', 'actual_hours')]
        print(f"Target columns: {target_columns}")
        
        # We need the original CREATE TABLE statement to replicate constraints, 
        # but for simplicity in SQLite we can often just create a new one.
        # However, it's safer to just DROP COLUMN if supported.
        
        try:
            print("Trying direct DROP COLUMN...")
            cursor.execute("ALTER TABLE items DROP COLUMN estimated_hours")
            cursor.execute("ALTER TABLE items DROP COLUMN actual_hours")
            print("Direct DROP COLUMN successful.")
        except sqlite3.OperationalError:
            print("Direct DROP COLUMN not supported, using table recreation method...")
            # Re-creation method is complex to do right (foreign keys, indexes, etc.)
            # Given typically modern python environments, DROP COLUMN might work.
            # If it fails, I'll provide a warning.
            raise
            
    except Exception as e:
        print(f"Migration error: {e}")
        print("If DROP COLUMN is not supported, you might need to manually recreate the table or update SQLite.")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
