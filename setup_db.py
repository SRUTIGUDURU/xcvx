import asyncio
from database import db_service

async def setup_database():
    print("Initializing database schema...")
    try:
        await db_service.init_db()
        print("Database schema created successfully!")
    except Exception as e:
        print(f"Error creating database schema: {str(e)}")

if __name__ == "__main__":
    asyncio.run(setup_database()) 