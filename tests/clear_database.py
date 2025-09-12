import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from api.core.database import engine


async def clear_all_tables():
    """Clear all tables from database."""

    print("🧹 Clearing all tables from database...")

    # Create async session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Drop all tables in public schema
            print("🗑️  Dropping all tables...")
            await session.execute(text("DROP SCHEMA public CASCADE"))
            print("✅ Public schema dropped")

            # Create new public schema
            print("🆕 Creating new public schema...")
            await session.execute(text("CREATE SCHEMA public"))
            print("✅ New public schema created")

            # Set permissions
            await session.execute(text("GRANT ALL ON SCHEMA public TO root"))
            await session.execute(text("GRANT ALL ON SCHEMA public TO public"))
            print("✅ Permissions set")

            await session.commit()
            print("🎉 Database cleared successfully!")
            print("💡 You can now run migrations: alembic upgrade head")

        except Exception as e:
            print(f"❌ Error clearing database: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            await session.rollback()
            raise


if __name__ == "__main__":
    print("⚠️  WARNING: This script will delete ALL tables from the database!")
    print("⚠️  Make sure you have a backup if you need to preserve data.")

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() in ["yes", "y", "tak", "t"]:
        try:
            asyncio.run(clear_all_tables())
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("❌ Operation failed.")
    else:
        print("❌ Operation cancelled.")
