"""renamed likes to total_likes in quote table

Revision ID: 8b2969f9ea14
Revises: 1dc9f0d182f0
Create Date: 2020-08-02 11:33:25.639499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b2969f9ea14'
down_revision = '1dc9f0d182f0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('quote', 'likes', nullable=False, new_column_name='total_likes')


def downgrade():
    op.alter_column('quote', 'total_likes', nullable=False, new_column_name='likes')
