from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Get PostgreSQL connection details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/findafriend")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Define models
class Questionnaire(Base):
    __tablename__ = "questionnaire"
    email = Column(String, primary_key=True)
    hobbies = Column(Text)
    topics = Column(Text)
    gender = Column(String)
    year = Column(String)
    purpose = Column(Text)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    group_name = Column(String)
    email = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

class Group(Base):
    __tablename__ = "groups"
    id = Column(String, primary_key=True)
    group_name = Column(String)
    email = Column(Text)

class DatabaseService:
    def __init__(self):
        self.engine = engine
        self.Base = Base

    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        async with AsyncSessionLocal() as session:
            yield session

    async def save_questionnaire(self, data: dict):
        async with AsyncSessionLocal() as session:
            questionnaire = Questionnaire(**data)
            session.add(questionnaire)
            await session.commit()

    async def get_questionnaire_data(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT * FROM questionnaire")
            rows = result.fetchall()
            return [dict(zip(result.keys(), row)) for row in rows]

    async def save_message(self, data: dict):
        async with AsyncSessionLocal() as session:
            message = Message(**data)
            session.add(message)
            await session.commit()

    async def get_messages(self, group_name: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM messages WHERE group_name = :group_name ORDER BY timestamp",
                {"group_name": group_name}
            )
            rows = result.fetchall()
            return [dict(zip(result.keys(), row)) for row in rows]

    async def save_groups(self, groups: list):
        async with AsyncSessionLocal() as session:
            for group_data in groups:
                group = Group(**group_data)
                session.add(group)
            await session.commit()

    async def get_groups(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT * FROM groups")
            rows = result.fetchall()
            return [dict(zip(result.keys(), row)) for row in rows]

# Create database service instance
db_service = DatabaseService() 