"""Add ethereum wallet to companies

Revision ID: <keep what's generated>
Revises: 5e3da7df7f2d
Create Date: <keep what's generated>

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '<keep whats generated>'
down_revision = '5e3da7df7f2d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('eth_address', sa.String(length=42), nullable=True))
        batch_op.add_column(sa.Column('eth_private_key', sa.String(length=66), nullable=True))
        batch_op.create_unique_constraint('uq_companies_eth_address', ['eth_address'])


def downgrade():
    with op.batch_alter_table('companies', schema=None) as batch_op:
        batch_op.drop_constraint('uq_companies_eth_address', type_='unique')
        batch_op.drop_column('eth_private_key')
        batch_op.drop_column('eth_address')