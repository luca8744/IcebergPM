import os
import sys
import csv
from sqlalchemy.orm import Session

# Add the project root to sys.path to allow importing from backend
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal, engine
from app.models import models
from app.core import security

def import_data(file_path: str):
    db = SessionLocal()
    try:
        # 1. Ensure the Client User exists
        client_username = "Eurosets"
        client = db.query(models.User).filter(models.User.username == client_username).first()
        
        if not client:
            print(f"Creating user {client_username}...")
            hashed_password = security.get_password_hash("eurosets123")
            client = models.User(
                username=client_username,
                hashed_password=hashed_password,
                role=models.UserRole.CLIENT,
                is_active=True
            )
            db.add(client)
            db.commit()
            db.refresh(client)
            print(f"User {client_username} created.")

        # 2. Read CSV
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return

        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            row_count = 0
            projects_cache = {} # Cache projects to avoid redundant queries

            for row in reader:
                p_name = row.get('project_name', '').strip()
                p_desc = row.get('project_description', '').strip()
                t_title = row.get('task_title', '').strip()
                t_desc = row.get('task_description', '').strip()
                t_status_raw = row.get('task_status', 'OPEN').strip().upper()
                
                if not p_name or not t_title:
                    continue

                # Get or Create Project
                if p_name not in projects_cache:
                    project = db.query(models.Project).filter(
                        models.Project.name == p_name,
                        models.Project.client_id == client.id
                    ).first()
                    
                    if not project:
                        print(f"Creating project: {p_name}")
                        project = models.Project(
                            name=p_name,
                            description=p_desc,
                            client_id=client.id
                        )
                        db.add(project)
                        db.commit()
                        db.refresh(project)
                    
                    projects_cache[p_name] = project.id

                # Map Status
                try:
                    status = models.ItemStatus(t_status_raw)
                except ValueError:
                    status = models.ItemStatus.OPEN

                # Create Item
                item = models.Item(
                    title=t_title,
                    description=t_desc,
                    status=status,
                    project_id=projects_cache[p_name],
                    internal_priority=models.ItemPriority.MEDIUM # Default
                )
                db.add(item)
                row_count += 1

            db.commit()
            print(f"Import completed! {row_count} tasks imported.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    csv_path = os.path.join("backend", "imports", "data.csv")
    import_data(csv_path)
