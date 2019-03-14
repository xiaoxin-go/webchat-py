"""empty message

Revision ID: ac0a67313a58
Revises: 42ff77c1f762
Create Date: 2019-03-12 21:26:56.380741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac0a67313a58'
down_revision = '42ff77c1f762'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('t_chat', sa.Column('message', sa.Text(), nullable=True))
    op.drop_constraint('t_chatmessage_ibfk_1', 't_chatmessage', type_='foreignkey')
    op.drop_constraint('t_groupuser_ibfk_2', 't_groupuser', type_='foreignkey')
    op.drop_constraint('t_groupuser_ibfk_1', 't_groupuser', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('t_groupuser_ibfk_1', 't_groupuser', 't_group', ['group_id'], ['id'])
    op.create_foreign_key('t_groupuser_ibfk_2', 't_groupuser', 't_user', ['user_id'], ['id'])
    op.create_foreign_key('t_chatmessage_ibfk_1', 't_chatmessage', 't_user', ['user_id'], ['id'])
    op.drop_column('t_chat', 'message')
    # ### end Alembic commands ###
