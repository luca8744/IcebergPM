import os
import sys
import csv
import traceback
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Add the project root to sys.path to allow importing from backend
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal, engine
from app.models import models
from app.core import security

def map_status(raw_status: str) -> models.ItemStatus:
    if not raw_status:
        return models.ItemStatus.OPEN
    
    raw_status = str(raw_status).strip().upper()
    if raw_status == "DONE":
        return models.ItemStatus.DONE
    if raw_status in ["RUNNING", "IN_PROGRESS"]:
        return models.ItemStatus.IN_PROGRESS
    if raw_status == "CLOSED":
        return models.ItemStatus.CLOSED
    # Default for 'Waiting', 'end feb', 'OPEN', etc.
    return models.ItemStatus.OPEN

def clean_data(db: Session, client_id: int):
    print(f"Cleaning existing data for client_id: {client_id}...")
    # Projects are linked to clients. Items are linked to projects.
    # Deleting projects will delete items due to cascade="all, delete-orphan"
    projects = db.query(models.Project).filter(models.Project.client_id == client_id).all()
    count = len(projects)
    for p in projects:
        db.delete(p)
    db.commit()
    print(f"Deleted {count} projects and their related items.")

def import_file(db: Session, file_path: str, client_id: int, projects_cache: Dict[str, int]):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return 0

    print(f"Importing {file_path}...")
    row_count = 0
    tag_cache = {}

    # Use latin-1 to handle special characters as found in research
    try:
        with open(file_path, mode='r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                # Clean keys to handle trailing spaces and potential None keys
                cleaned_row = {str(k).strip() if k else "": v for k, v in row.items()}
                
                # Check for project name in common variations
                p_name = cleaned_row.get('Project Name', '').strip() or \
                         cleaned_row.get('Project name', '').strip()
                
                if not p_name or p_name.lower() == 'project name':
                    continue

                # Get or Create Project
                if p_name not in projects_cache:
                    project = db.query(models.Project).filter(
                        models.Project.name == p_name,
                        models.Project.client_id == client_id
                    ).first()
                    
                    if not project:
                        print(f"Creating project: {p_name}")
                        project = models.Project(
                            name=p_name,
                            client_id=client_id
                        )
                        db.add(project)
                        db.flush()
                    
                    projects_cache[p_name] = project.id

                project_id = projects_cache[p_name]

                # Map Task Title and Description
                t_title = cleaned_row.get('Task Title', '').strip()
                t_desc = cleaned_row.get('Task Description', '').strip()
                
                # Handling File 2 where Task Description is effectively the title
                if not t_title and t_desc:
                    t_title = t_desc
                    t_desc = ""
                
                if not t_title:
                    continue

                # Map Status
                raw_status = cleaned_row.get('STATUS', '').strip() or \
                             cleaned_row.get('Status', '').strip() or 'OPEN'
                status = map_status(raw_status)
                
                # Map Internal and Requirement fields
                internal_notes = cleaned_row.get('Note interne', '').strip()
                ext_id = cleaned_row.get('Ext', '').strip()
                hlr = cleaned_row.get('HLR', '').strip()
                srs = cleaned_row.get('SRS', '').strip()
                tp = cleaned_row.get('TP', '').strip()
                tag_str = cleaned_row.get('TAG', '').strip()

                # Create Item
                item = models.Item(
                    title=t_title,
                    description=t_desc,
                    status=status,
                    project_id=project_id,
                    internal_notes=internal_notes,
                    external_id=ext_id,
                    hlr=hlr,
                    srs=srs,
                    tp=tp,
                    internal_priority=models.ItemPriority.MEDIUM
                )
                db.add(item)
                db.flush()

                # Handle Tags
                if tag_str:
                    # Support multiple tags separated by comma or semicolon
                    tags = [t.strip() for t in tag_str.replace(',', ';').split(';') if t.strip()]
                    for t_name in tags:
                        if t_name not in tag_cache:
                            tag = db.query(models.Tag).filter(models.Tag.name == t_name).first()
                            if not tag:
                                tag = models.Tag(name=t_name)
                                db.add(tag)
                                db.flush()
                            tag_cache[t_name] = tag
                        item.tags.append(tag_cache[t_name])

                row_count += 1
                if row_count % 100 == 0:
                    print(f"  Processed {row_count} rows...")

        db.commit()
        print(f"Finished {file_path}: {row_count} tasks imported.")
        return row_count
    except Exception as e:
        db.rollback()
        print(f"Error importing {file_path}: {e}")
        traceback.print_exc()
        return 0

def run_import():
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

        # 2. Cleanup existing data (Replace logic)
        clean_data(db, client.id)

        # 3. Import target files
        datasource_dir = "datasource"
        files_to_import = [
            os.path.join(datasource_dir, "BUG&Improvement HLM_02_LB.csv"),
            os.path.join(datasource_dir, "EU_activities_2026 1_LB.csv")
        ]
        
        projects_cache = {}
        total_count = 0
        for file_path in files_to_import:
            total_count += import_file(db, file_path, client.id, projects_cache)

        print(f"\nSUCCESS: Total {total_count} tasks imported into {len(projects_cache)} projects.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_import()

