import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time


SQLALCHEMY_DATABASE_URL = "postgresql://humayun:testpassword@localhost/project"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# while True:
#     try:
#         conn=psycopg2.connect(host='localhost',database='project',user='humayun',
#                           password='testpassword', cursor_factory=RealDictCursor)
#         cursor=conn.cursor()
#         print("Database connected")
#         break
#     except Exception as error:
#         print("Connection to database failed")
#         print("Error:", error)
#         time.sleep(2)

