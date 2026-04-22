import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Aggiungi la cartella radice al path per importare i modelli se necessario
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

# Caricamento .env
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    default_db_path = os.path.join(BASE_DIR, "iceberg_pm.db")
    DATABASE_URL = f"sqlite:///{default_db_path}"

def migrate():
    print(f"Migrating database: {DATABASE_URL} (V5)...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        
        # 1. Create clients table
        print("Creating 'clients' table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY if 'postgresql' in engine.url.drivername else INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """.replace("SERIAL PRIMARY KEY if 'postgresql' in engine.url.drivername else INTEGER PRIMARY KEY AUTOINCREMENT", 
                   "SERIAL PRIMARY KEY" if "postgresql" in DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT")))

        # 2. Check if client_id exists in users
        users_columns = [c['name'] for c in inspector.get_columns('users')]
        if 'client_id' not in users_columns:
            print("Adding 'client_id' column to 'users'...")
            if "postgresql" in DATABASE_URL:
                conn.execute(text("ALTER TABLE users ADD COLUMN client_id INTEGER REFERENCES clients(id)"))
            else:
                conn.execute(text("ALTER TABLE users ADD COLUMN client_id INTEGER"))
        
        # 3. Extract unique reference_client from users and insert into clients
        if 'reference_client' in users_columns:
            print("Migrating unique reference_clients to 'clients' table...")
            unique_clients = conn.execute(text("SELECT DISTINCT reference_client FROM users WHERE reference_client IS NOT NULL AND reference_client != ''")).fetchall()
            
            for row in unique_clients:
                client_name = row[0]
                print(f" - Found client: {client_name}")
                conn.execute(text("INSERT INTO clients (name) VALUES (:name) ON CONFLICT (name) DO NOTHING" if "postgresql" in DATABASE_URL else "INSERT OR IGNORE INTO clients (name) VALUES (:name)"), {"name": client_name})

            # 4. Populate users.client_id based on reference_client
            print("Linking users to clients...")
            users_to_update = conn.execute(text("SELECT id, reference_client FROM users WHERE reference_client IS NOT NULL AND reference_client != ''")).fetchall()
            for u_id, ref_client in users_to_update:
                client_row = conn.execute(text("SELECT id FROM clients WHERE name = :name"), {"name": ref_client}).fetchone()
                if client_row:
                    conn.execute(text("UPDATE users SET client_id = :c_id WHERE id = :u_id"), {"c_id": client_row[0], "u_id": u_id})

        # 5. Handle projects table
        # We need to change client_id from User ID to Client ID
        print("Migrating 'projects' table ownership...")
        
        # Backup projects
        conn.execute(text("DROP TABLE IF EXISTS projects_old"))
        if "postgresql" in DATABASE_URL:
            conn.execute(text("CREATE TABLE projects_old AS SELECT * FROM projects"))
        else:
            conn.execute(text("CREATE TABLE projects_old AS SELECT * FROM projects"))

        # Map old user_id -> new client_id
        user_to_client_map = {}
        mapped_users = conn.execute(text("SELECT id, client_id FROM users WHERE client_id IS NOT NULL")).fetchall()
        for u_id, c_id in mapped_users:
            user_to_client_map[u_id] = c_id

        # Drop and recreate projects table with new FK
        conn.execute(text("DROP TABLE projects CASCADE" if "postgresql" in DATABASE_URL else "DROP TABLE projects"))
        
        project_table_sql = """
            CREATE TABLE projects (
                id SERIAL PRIMARY KEY if 'postgresql' in engine.url.drivername else INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """.replace("SERIAL PRIMARY KEY if 'postgresql' in engine.url.drivername else INTEGER PRIMARY KEY AUTOINCREMENT", 
                   "SERIAL PRIMARY KEY" if "postgresql" in DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT")
        
        conn.execute(text(project_table_sql))

        # Migrate data from backup
        old_projects = conn.execute(text("SELECT id, name, description, client_id, created_at FROM projects_old")).fetchall()
        for p_id, name, desc, old_client_user_id, created_at in old_projects:
            new_client_id = user_to_client_map.get(old_client_user_id)
            
            if new_client_id is None:
                # If the user wasn't a client with a reference_client, 
                # we create a client named after the user to preserve integrity
                user_row = conn.execute(text("SELECT username FROM users WHERE id = :id"), {"id": old_client_user_id}).fetchone()
                if user_row:
                    username = user_row[0]
                    conn.execute(text("INSERT INTO clients (name) VALUES (:name) ON CONFLICT (name) DO NOTHING" if "postgresql" in DATABASE_URL else "INSERT OR IGNORE INTO clients (name) VALUES (:name)"), {"name": username})
                    client_row = conn.execute(text("SELECT id FROM clients WHERE name = :name"), {"name": username}).fetchone()
                    new_client_id = client_row[0]
                    # Link the user to this new client too
                    conn.execute(text("UPDATE users SET client_id = :c_id WHERE id = :u_id"), {"c_id": new_client_id, "u_id": old_client_user_id})
            
            if new_client_id:
                conn.execute(text("""
                    INSERT INTO projects (id, name, description, client_id, created_at)
                    VALUES (:id, :name, :desc, :c_id, :created_at)
                """), {"id": p_id, "name": name, "desc": desc, "c_id": new_client_id, "created_at": created_at})
            else:
                print(f"Warning: Project {name} (ID {p_id}) lost its client link.")

        conn.execute(text("DROP TABLE projects_old"))
        print("Migration V5 completed successfully.")

if __name__ == "__main__":
    migrate()
