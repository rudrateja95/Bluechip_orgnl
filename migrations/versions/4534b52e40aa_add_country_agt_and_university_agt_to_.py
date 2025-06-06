"""Add country_agt and university_agt to AgentDoc

Revision ID: 4534b52e40aa
Revises: 548cd2b8ad6a
Create Date: 2024-11-11 15:33:44.461845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4534b52e40aa'
down_revision = '548cd2b8ad6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('agents_doc', schema=None) as batch_op:
        batch_op.add_column(sa.Column('country_agt', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('university_agt', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('agents_doc', schema=None) as batch_op:
        batch_op.drop_column('university_agt')
        batch_op.drop_column('country_agt')

    # ### end Alembic commands ###
