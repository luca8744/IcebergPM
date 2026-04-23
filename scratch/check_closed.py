import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./iceberg_pm.db"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    res = conn.execute(text("SELECT COUNT(*) FROM items WHERE status = 'CLOSED'"))
    count = res.fetchone()[0]
    print(f"CLOSED_COUNT: {count}")
