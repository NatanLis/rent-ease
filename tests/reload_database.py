#!/usr/bin/env python3
"""
Reload Database Script

This script clears the database, runs migrations, and loads test seeds.
Equivalent to running:
1. python -m tests.clear_database
2. alembic upgrade head
3. python -m tests.load_seeds
"""

import asyncio
import subprocess
import sys
from pathlib import Path

import asyncpg
import httpx

from api.core.config import settings
from tests.clear_database import clear_all_tables
from tests.load_seeds import load_seeds

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def load_profile_pictures():
    """Load profile pictures from Pravatar for all users."""
    # Use the DATABASE_URL from settings, but convert to asyncpg format
    DATABASE_URL = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql://"
    )

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # Get all users
        users = await conn.fetch(
            "SELECT id, first_name, last_name, email FROM users ORDER BY id"
        )
        print(f"📊 Found {len(users)} users")

        if not users:
            print("⚠️ No users found in database")
            return

        # Download and upload profile pictures
        async with httpx.AsyncClient() as client:
            for user in users:
                user_id = user["id"]
                print(
                    f"🔄 Processing user {user_id}: {user['first_name']} {user['last_name']}"
                )

                # Download image from Pravatar
                url = f"https://i.pravatar.cc/128?u={user_id}"
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        image_data = response.content

                        # Insert profile picture
                        profile_picture_id = await conn.fetchval(
                            """
                            INSERT INTO profile_pictures (user_id, filename, mimetype, size, data, created_at)
                            VALUES ($1, $2, $3, $4, $5, NOW())
                            RETURNING id
                        """,
                            user_id,
                            f"profile_{user_id}.jpg",
                            "image/jpeg",
                            len(image_data),
                            image_data,
                        )

                        # Update user with profile_picture_id
                        await conn.execute(
                            """
                            UPDATE users
                            SET profile_picture_id = $1, updated_at = NOW()
                            WHERE id = $2
                        """,
                            profile_picture_id,
                            user_id,
                        )

                        print(f"  ✅ Added profile picture (ID: {profile_picture_id})")
                    else:
                        print(
                            f"  ❌ Failed to download image (HTTP {response.status_code})"
                        )

                except Exception as e:
                    print(f"  ❌ Error: {str(e)}")

                # Small delay
                await asyncio.sleep(0.5)

        await conn.close()

    except Exception as e:
        print(f"❌ Error loading profile pictures: {str(e)}")


async def reload_database():
    """Reload database: clear, migrate, and seed."""
    print("🔄 Reloading database...")
    print("=" * 50)

    try:
        # Step 1: Clear database
        print("🧹 Step 1: Clearing database...")
        await clear_all_tables()
        print("✅ Database cleared successfully!")
        print()

        # Step 2: Run migrations
        print("📦 Step 2: Running migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
        else:
            print("❌ Migration failed!")
            print(f"Error: {result.stderr}")
            return False
        print()

        # Step 3: Load seeds
        print("🌱 Step 3: Loading test seeds...")
        await load_seeds()
        print("✅ Seeds loaded successfully!")
        print()

        # Step 4: Load profile pictures
        print("🖼️ Step 4: Loading profile pictures...")
        await load_profile_pictures()
        print("✅ Profile pictures loaded successfully!")
        print()

        print("🎉 Database reload completed successfully!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"❌ Error during database reload: {str(e)}")
        print("=" * 50)
        return False


def main():
    """Main function."""
    print("⚠️  WARNING: This script will delete ALL data from the database!")
    print("⚠️  Make sure you have a backup if you need to preserve data.")
    print()

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() not in ["yes", "y", "tak", "t"]:
        print("❌ Operation cancelled.")
        return

    print()
    success = asyncio.run(reload_database())

    if success:
        print("🚀 Database is ready to use!")
    else:
        print("💥 Database reload failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
