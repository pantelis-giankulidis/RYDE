from sqlalchemy.orm import declarative_base 
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

Base = declarative_base()
load_dotenv()

async_session = async_sessionmaker(autocommit = False, autoflush = False, bind = create_async_engine(os.getenv("SQL_ALCHEMY_DATABASE_URL_ASYNC")))

async def get_batabase_session():
    async with async_session() as session:
        yield session 