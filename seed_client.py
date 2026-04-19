from backend.app.database import SessionLocal
from backend.app.models import models
from backend.app.core.security import get_password_hash

def seed_client():
    db = SessionLocal()
    try:
        # Create a test client
        client = db.query(models.User).filter(models.User.username == "cliente1").first()
        if not client:
            client = models.User(
                username="cliente1",
                hashed_password=get_password_hash("cliente123"),
                role=models.UserRole.CLIENT
            )
            db.add(client)
            db.commit()
            print("Cliente creato: cliente1 / cliente123 (ID: 2)")
        else:
            print("Il cliente esiste già.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_client()
