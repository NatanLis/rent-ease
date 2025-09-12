#!/usr/bin/env python3
"""
Script to download profile pictures from database and save them to downloads folder.
"""

import asyncio
import sys
from pathlib import Path

# Add API path to sys.path
sys.path.append(str(Path(__file__).parent.parent / "api"))

from sqlalchemy import select

from api.core.database import get_session
from api.src.profile_pictures.models import ProfilePicture

# Import all models to fix SQLAlchemy relationships


async def download_profile_pictures():
    """Download all profile pictures from database and save them to downloads folder."""

    # Create downloads folder if it doesn't exist
    downloads_dir = Path(__file__).parent / "downloads"
    downloads_dir.mkdir(exist_ok=True)

    print(f"📁 Downloads folder: {downloads_dir}")

    # Get database session
    async for session in get_session():
        try:
            # Get all profile pictures
            result = await session.execute(select(ProfilePicture))
            profile_pictures = result.scalars().all()

            if not profile_pictures:
                print("❌ No profile pictures found in database")
                return

            print(f"📸 Found {len(profile_pictures)} profile pictures")

            # Save each picture
            for pic in profile_pictures:
                # Create filename
                filename = f"profile_{pic.user_id}_{pic.filename}"
                filepath = downloads_dir / filename

                # Save binary data to file
                with open(filepath, "wb") as f:
                    f.write(pic.data)

                print(f"✅ Saved: {filename} ({pic.size} bytes, {pic.mimetype})")

            print(f"\n🎉 All pictures saved to: {downloads_dir}")

        except Exception as e:
            print(f"❌ Error downloading pictures: {e}")
        finally:
            await session.close()
        break


if __name__ == "__main__":
    print("🚀 Downloading profile pictures from database...")
    asyncio.run(download_profile_pictures())
