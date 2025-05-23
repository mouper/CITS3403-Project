"""Add invite tables

Revision ID: 9397a8d126fd
Revises: cf6db34f8c31
Create Date: 2025-05-11 22:37:43.614969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9397a8d126fd'
down_revision = 'cf6db34f8c31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tournament_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invite')
    # ### end Alembic commands ###
