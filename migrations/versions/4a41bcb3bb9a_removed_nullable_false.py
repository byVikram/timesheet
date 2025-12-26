"""removed nullable false

Revision ID: 4a41bcb3bb9a
Revises: 1c352ba832d5
Create Date: 2025-12-05 14:06:38.822679

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4a41bcb3bb9a'
down_revision = '1c352ba832d5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('timesheet_entries', schema=None) as batch_op:
        # Drop foreign key first
        batch_op.drop_constraint('timesheet_entries_ibfk_5', type_='foreignkey')
        
        # Alter column
        batch_op.alter_column('status',
               existing_type=mysql.INTEGER(),
               nullable=False)
        
        # Re-create foreign key
        batch_op.create_foreign_key(
            'timesheet_entries_ibfk_5',  # same name as before
            'timesheet_status',          # referenced table
            ['status'],                  # local column
            ['id']                       # referenced column
        )

def downgrade():
    with op.batch_alter_table('timesheet_entries', schema=None) as batch_op:
        batch_op.drop_constraint('timesheet_entries_ibfk_5', type_='foreignkey')
        batch_op.alter_column('status',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.create_foreign_key(
            'timesheet_entries_ibfk_5',
            'timesheet_status',
            ['status'],
            ['id']
        )


    # ### end Alembic commands ###
