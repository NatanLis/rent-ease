"""load_profile_pictures

Revision ID: def456ghi789
Revises: abc123def456
Create Date: 2025-09-09 16:45:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "def456ghi789"
down_revision: Union[str, None] = "abc123def456"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add profile pictures for users."""
    print("🖼️ Setting up profile pictures...")

    # Create a simple placeholder profile picture for each user
    # In development, you can later run the reload_database script to get real Pravatar images
    op.execute("""
        WITH user_pics AS (
            SELECT u.id as user_id,
                   'profile_' || u.id || '.jpg' as filename,
                   'image/jpeg' as mimetype,
                   1024 as size,
                   decode('FFD8FFE000104A46494600010101006000600000FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C2837292C30313434341F27393D38323C2E333432FFDB0043010909090C0B0C180D0D1832211C213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232FFC0001108001000010101110000021101031101FFC4001F0000010501010101010100000000000000000102030405060708090A0BFFC400B5100002010303020403050504040000017D01020300041105122131410613516107227114328191A1082342B1C11552D1F02433627282090A161718191A25262728292A3435363738393A434445464748494A535455565758595A636465666768696A737475767778797A838485868788898A92939495969798999AA2A3A4A5A6A7A8A9AAB2B3B4B5B6B7B8B9BAC2C3C4C5C6C7C8C9CAD2D3D4D5D6D7D8D9DAE1E2E3E4E5E6E7E8E9EAF1F2F3F4F5F6F7F8F9FAFFC4001F0100030101010101010101010000000000000102030405060708090A0BFFC400B51100020102040403040705040400010277000102031104052131061241510761711322328108144291A1B1C109233352F0156272D10A162434E125F11718191A262728292A35363738393A434445464748494A535455565758595A636465666768696A737475767778797A82838485868788898A92939495969798999AA2A3A4A5A6A7A8A9AAB2B3B4B5B6B7B8B9BAC2C3C4C5C6C7C8C9CAD2D3D4D5D6D7D8D9DAE2E3E4E5E6E7E8E9EAF2F3F4F5F6F7F8F9FAFFDA000C03010002110311003F00FFD9', 'hex') as data
            FROM users u
            WHERE u.profile_picture_id IS NULL
        ),
        inserted_pics AS (
            INSERT INTO profile_pictures (user_id, filename, mimetype, size, data, created_at)
            SELECT user_id, filename, mimetype, size, data, NOW()
            FROM user_pics
            RETURNING id, user_id
        )
        UPDATE users
        SET profile_picture_id = inserted_pics.id, updated_at = NOW()
        FROM inserted_pics
        WHERE users.id = inserted_pics.user_id;
    """)

    print("✅ Profile pictures added!")


def downgrade() -> None:
    """Remove profile pictures."""
    print("🧹 Removing profile pictures...")

    # Remove profile picture references from users
    op.execute("UPDATE users SET profile_picture_id = NULL, updated_at = NOW()")

    # Remove all profile pictures
    op.execute("DELETE FROM profile_pictures")

    print("✅ Profile pictures removed!")
