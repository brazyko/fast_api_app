"""2

Revision ID: c3c39df68d0f
Revises: 12b110228979
Create Date: 2024-09-17 23:54:45.653839

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3c39df68d0f'
down_revision = '12b110228979'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('preferences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('color_scheme', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('notifications_on', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preferences_color_scheme'), 'preferences', ['color_scheme'], unique=False)
    op.create_index(op.f('ix_preferences_id'), 'preferences', ['id'], unique=False)
    op.create_index(op.f('ix_preferences_user_id'), 'preferences', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_preferences_user_id'), table_name='preferences')
    op.drop_index(op.f('ix_preferences_id'), table_name='preferences')
    op.drop_index(op.f('ix_preferences_color_scheme'), table_name='preferences')
    op.drop_table('preferences')
    # ### end Alembic commands ###