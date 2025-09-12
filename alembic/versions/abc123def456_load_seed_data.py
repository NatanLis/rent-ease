"""load_seed_data

Revision ID: abc123def456
Revises: 91506d06f6fd
Create Date: 2025-09-09 16:30:00.000000

"""

import json
from datetime import datetime
from pathlib import Path
from typing import Sequence, Union

import bcrypt

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abc123def456"
down_revision: Union[str, None] = "55b76e70a9f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


def upgrade() -> None:
    """Load seed data into database."""
    print("🌱 Loading seed data...")

    project_root = get_project_root()
    seeds_dir = project_root / "tests" / "seeds"

    # Load users
    print("👥 Loading users...")
    users_file = seeds_dir / "users_test_data.json"
    if users_file.exists():
        with open(users_file) as f:
            users_data = json.load(f)

        for user_data in users_data:
            # Skip admin user as it's already created in previous migration
            if user_data["email"] == "admin@rent-ease.com":
                continue

            hashed_password = get_password_hash(user_data["password"])
            created_at = datetime.fromisoformat(
                user_data.get("created_at", datetime.now().isoformat()).replace(
                    "Z", "+00:00"
                )
            )

            op.execute(f"""
                INSERT INTO users (email, hashed_password, first_name, last_name, username, role, is_active, created_at)
                VALUES ('{user_data["email"]}', '{hashed_password}', '{user_data["first_name"]}',
                       '{user_data["last_name"]}', '{user_data["username"]}', '{user_data["role"]}',
                       {user_data.get("is_active", True)}, '{created_at}')
                ON CONFLICT (email) DO NOTHING
            """)

    # Load properties
    print("🏠 Loading properties...")
    properties_file = seeds_dir / "properties_test_data.json"
    if properties_file.exists():
        with open(properties_file) as f:
            properties_data = json.load(f)

        for prop_data in properties_data:
            # Get owner_id from email
            op.execute(f"""
                INSERT INTO properties (title, description, address, price, owner_id)
                SELECT '{prop_data["title"]}', '{prop_data["description"]}',
                       '{prop_data["address"]}', {prop_data["price"]}, u.id
                FROM users u
                WHERE u.email = '{prop_data["owner_email"]}'
                AND NOT EXISTS (SELECT 1 FROM properties WHERE title = '{prop_data["title"]}')
            """)

    # Load units
    print("🏢 Loading units...")
    units_file = seeds_dir / "units_test_data.json"
    if units_file.exists():
        with open(units_file) as f:
            units_data = json.load(f)

        for unit_data in units_data:
            op.execute(f"""
                INSERT INTO units (name, description, monthly_rent, property_id)
                SELECT '{unit_data["name"]}', '{unit_data["description"]}',
                       {unit_data["monthly_rent"]}, p.id
                FROM properties p
                WHERE p.title = '{unit_data["property_title"]}'
                AND NOT EXISTS (SELECT 1 FROM units WHERE name = '{unit_data["name"]}' AND property_id = p.id)
            """)

    # Load leases
    print("📋 Loading leases...")
    leases_file = seeds_dir / "leases_test_data.json"
    if leases_file.exists():
        with open(leases_file) as f:
            leases_data = json.load(f)

        for lease_data in leases_data:
            start_date = datetime.fromisoformat(
                lease_data["start_date"].replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(
                lease_data["end_date"].replace("Z", "+00:00")
            )

            op.execute(f"""
                INSERT INTO leases (start_date, end_date, is_active, unit_id, tenant_id)
                SELECT '{start_date}', '{end_date}', {lease_data["is_active"]}, u.id, t.id
                FROM units u
                CROSS JOIN users t
                INNER JOIN properties p ON u.property_id = p.id
                WHERE u.name = '{lease_data["unit_name"]}'
                AND p.title = '{lease_data["property_title"]}'
                AND t.email = '{lease_data["tenant_email"]}'
                AND NOT EXISTS (SELECT 1 FROM leases WHERE unit_id = u.id AND tenant_id = t.id)
            """)

    # Load sample files
    print("📁 Loading sample files...")
    sample_files_dir = seeds_dir / "sample_files"
    if sample_files_dir.exists():
        pdf_files = list(sample_files_dir.glob("*.pdf"))

        for pdf_file in pdf_files[:3]:  # Limit to 3 files
            if not pdf_file.name.endswith(":Zone.Identifier"):
                with open(pdf_file, "rb") as f:
                    file_data = f.read()

                # Convert binary data to hex string for SQL
                hex_data = file_data.hex()

                op.execute(f"""
                    INSERT INTO files (filename, mimetype, size, data, created_at)
                    VALUES ('{pdf_file.name}', 'application/pdf', {len(file_data)},
                           decode('{hex_data}', 'hex'), NOW())
                    ON CONFLICT DO NOTHING
                """)

    print("✅ Seed data loaded successfully!")


def downgrade() -> None:
    """Remove seed data from database."""
    print("🧹 Removing seed data...")

    # Remove in reverse order due to foreign key constraints
    op.execute("DELETE FROM leases WHERE id > 0")
    op.execute("DELETE FROM units WHERE id > 0")
    op.execute("DELETE FROM properties WHERE id > 0")
    op.execute("DELETE FROM files WHERE id > 0")
    op.execute("DELETE FROM users WHERE email != 'admin@rent-ease.com'")

    print("✅ Seed data removed!")
