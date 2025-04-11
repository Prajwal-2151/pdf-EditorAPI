from db import Base, engine, SessionLocal
from models import User
from sqlalchemy import text

# Create new tables (does NOT update existing tables)
print("Creating missing tables...")
Base.metadata.create_all(bind=engine)

# Modify existing tables manually
print("Checking and altering existing tables if needed...")
with engine.connect() as conn:
          # Check if 'session_token' exists in 'users' table
          result = conn.execute(
                    text("SHOW COLUMNS FROM users LIKE 'session_token'")
          ).fetchone()

          if not result:
                    print("Adding 'session_token' column to users table...")
                    conn.execute(
                              text("ALTER TABLE users ADD COLUMN session_token VARCHAR(255)")
                    )
          else:
                    print("'session_token' column already exists.")

print("Done.")
