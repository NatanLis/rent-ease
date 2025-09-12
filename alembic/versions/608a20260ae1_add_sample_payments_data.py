"""add_sample_payments_data

Revision ID: 608a20260ae1
Revises: 21c5a03aba1d
Create Date: 2025-09-10 21:06:40.887238

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "608a20260ae1"
down_revision: Union[str, None] = "21c5a03aba1d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add sample payments data."""
    print("💰 Loading sample payments data...")

    # Sample payments data based on existing leases
    payments_data = [
        # PAID payments
        {
            "document_type": "Rent Invoice",
            "gross_value": 2500.0,
            "due_date": "2024-08-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for August 2024",
            "is_paid": True,
            "unit_name": "A1",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Rent Invoice",
            "gross_value": 3200.0,
            "due_date": "2024-08-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for August 2024",
            "is_paid": True,
            "unit_name": "A2",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Security Deposit",
            "gross_value": 5000.0,
            "due_date": "2024-01-15",
            "receiver": "Tenant 2",
            "description": "Security deposit for lease",
            "is_paid": True,
            "unit_name": "A1",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        # OVERDUE payments (due dates in the past, not paid)
        {
            "document_type": "Rent Invoice",
            "gross_value": 2500.0,
            "due_date": "2025-08-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for August 2025 - OVERDUE",
            "is_paid": False,
            "unit_name": "A1",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Rent Invoice",
            "gross_value": 4000.0,
            "due_date": "2025-07-15",
            "receiver": "Tenant 2",
            "description": "Monthly rent for July 2025 - OVERDUE",
            "is_paid": False,
            "unit_name": "Dom",
            "property_title": "Dom jednorodzinny",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Maintenance Fee",
            "gross_value": 500.0,
            "due_date": "2025-08-15",
            "receiver": "Tenant 2",
            "description": "Maintenance fee - OVERDUE",
            "is_paid": False,
            "unit_name": "A2",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        # PENDING payments (due dates in the future, not paid)
        {
            "document_type": "Rent Invoice",
            "gross_value": 2500.0,
            "due_date": "2025-10-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for October 2025",
            "is_paid": False,
            "unit_name": "A1",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Rent Invoice",
            "gross_value": 2800.0,
            "due_date": "2025-10-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for October 2025",
            "is_paid": False,
            "unit_name": "M1",
            "property_title": "Mieszkanie 3-pokojowe",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Rent Invoice",
            "gross_value": 4000.0,
            "due_date": "2025-11-01",
            "receiver": "Tenant 2",
            "description": "Monthly rent for November 2025",
            "is_paid": False,
            "unit_name": "Dom",
            "property_title": "Dom jednorodzinny",
            "tenant_email": "tenant2@example.com",
        },
        {
            "document_type": "Other",
            "gross_value": 300.0,
            "due_date": "2025-10-15",
            "receiver": "Tenant 1",
            "description": "Utility bill payment",
            "is_paid": False,
            "unit_name": "A1",
            "property_title": "Apartament w centrum",
            "tenant_email": "tenant1@example.com",
        },
    ]

    # Insert payments
    for payment in payments_data:
        op.execute(f"""
            INSERT INTO payments (
                document_type, gross_value, due_date, receiver, description,
                is_paid, lease_id, created_at, updated_at
            )
            SELECT
                '{payment["document_type"]}',
                {payment["gross_value"]},
                '{payment["due_date"]}',
                '{payment["receiver"]}',
                '{payment["description"]}',
                {payment["is_paid"]},
                l.id,
                NOW(),
                NOW()
            FROM leases l
            INNER JOIN units u ON l.unit_id = u.id
            INNER JOIN properties p ON u.property_id = p.id
            INNER JOIN users t ON l.tenant_id = t.id
            WHERE u.name = '{payment["unit_name"]}'
            AND p.title = '{payment["property_title"]}'
            AND t.email = '{payment["tenant_email"]}'
            AND l.is_active = true
            LIMIT 1
        """)

    print("✅ Sample payments data loaded successfully!")


def downgrade() -> None:
    """Remove sample payments data."""
    print("🧹 Removing sample payments data...")
    op.execute("DELETE FROM payments WHERE id > 0")
    print("✅ Sample payments data removed!")
