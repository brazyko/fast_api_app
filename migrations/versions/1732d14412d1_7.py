"""7

Revision ID: 1732d14412d1
Revises: 953b1d3340e7
Create Date: 2024-09-21 13:50:50.021139

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1732d14412d1'
down_revision = '953b1d3340e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('last_message', sa.String(length=2048), nullable=True))
    op.add_column('chats', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('chats', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index(op.f('ix_chats_id'), 'chats', ['id'], unique=False)
    op.create_index(op.f('ix_chats_id'), 'chats', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_chats_user_id'), table_name='chats')
    op.drop_index(op.f('ix_chats_id'), table_name='chats')
    op.drop_column('chats', 'updated_at')
    op.drop_column('chats', 'created_at')
    op.drop_column('chats', 'last_message')
    # ### end Alembic commands ###
