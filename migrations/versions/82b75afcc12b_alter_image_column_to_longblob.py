"""Alter image column to LONGBLOB

Revision ID: 82b75afcc12b
Revises: 14a87445306b
Create Date: 2024-11-07 17:46:40.267391

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '82b75afcc12b'
down_revision = '14a87445306b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bluechip_data', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=sa.BLOB(),
               type_=mysql.LONGBLOB(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bluechip_data', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=mysql.LONGBLOB(),
               type_=sa.BLOB(),
               nullable=False)

    # ### end Alembic commands ###
