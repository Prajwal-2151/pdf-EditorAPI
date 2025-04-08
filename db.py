from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual DB credentials
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:droxOdxRVzuNFIUAoOMDAwwTmhNmhfzR@switchyard.proxy.rlwy.net:13541/railway"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
