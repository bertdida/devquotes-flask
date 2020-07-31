"""renamed quote_type to quote_status

Revision ID: 4a3fb4478471
Revises: f9f0cf21d05c
Create Date: 2020-07-31 15:26:08.226651

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '4a3fb4478471'
down_revision = 'f9f0cf21d05c'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('quote_type', 'quote_status')

    op.execute('ALTER TABLE quote_status DROP CONSTRAINT quote_type_pkey CASCADE')
    op.create_primary_key('quote_status_pkey', 'quote_status', ['id'])

    op.drop_constraint('quote_type_name_key', 'quote_status', type_='unique')
    op.create_unique_constraint('quote_status_name_key', 'quote_status', ['name'])

    op.alter_column('quote', 'type_id', nullable=False, new_column_name='status_id')
    op.create_foreign_key('quote_status_id_fkey', 'quote', 'quote_status', ['status_id'], ['id'])


def downgrade():
    op.rename_table('quote_status', 'quote_type')

    op.execute('ALTER TABLE quote_type DROP CONSTRAINT quote_status_pkey CASCADE')
    op.create_primary_key('quote_type_pkey', 'quote_type', ['id'])

    op.drop_constraint('quote_status_name_key', 'quote_type', type_='unique')
    op.create_unique_constraint('quote_type_name_key', 'quote_type', ['name'])

    op.alter_column('quote', 'status_id', nullable=False, new_column_name='type_id')
    op.create_foreign_key('quote_type_id_fkey', 'quote', 'quote_type', ['type_id'], ['id'])
