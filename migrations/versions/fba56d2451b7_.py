"""empty message

Revision ID: fba56d2451b7
Revises: 9e110cfad0ef
Create Date: 2019-02-13 16:13:13.823696

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fba56d2451b7'
down_revision = '9e110cfad0ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('t_user', sa.Column('type', sa.Integer(), nullable=True))
    op.drop_column('t_user', 'is_admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('t_user', sa.Column('is_admin', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('t_user', 'type')
    # ### end Alembic commands ###
