"""create files table

Revision ID: 445f7ca1bb11
Revises: 3cdc333b3266
Create Date: 2025-08-20 17:43:46.558793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '445f7ca1bb11'
down_revision: Union[str, None] = '3cdc333b3266'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'files',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.Text, nullable=False),
        sa.Column('mimetype', sa.Text, nullable=False),
        sa.Column('size', sa.Integer, nullable=False),
        sa.Column('data', sa.LargeBinary, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('files')
