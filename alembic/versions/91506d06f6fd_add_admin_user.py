"""add_admin_user

Revision ID: 91506d06f6fd
Revises: 445f7ca1bb11
Create Date: 2025-09-01 13:24:59.230785

"""

import os
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "91506d06f6fd"
down_revision: Union[str, None] = "445f7ca1bb11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get admin data from environment variables
    admin_email = os.getenv("ADMIN_EMAIL", "admin@rent-ease.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    # Hash the password (using bcrypt)
    import bcrypt

    hashed_password = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Add admin user
    op.execute(
        f"""
        INSERT INTO users (email, hashed_password, role) VALUES
        ('{admin_email}', '{hashed_password}', 'ADMIN')
        ON CONFLICT (email) DO NOTHING
    """
    )


def downgrade() -> None:
    # Remove admin user
    admin_email = os.getenv("ADMIN_EMAIL", "admin@rent-ease.com")
    op.execute(f"DELETE FROM users WHERE email = '{admin_email}'")
