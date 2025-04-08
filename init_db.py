from db import Base, engine
from models import User

# Create all tables in the database
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
