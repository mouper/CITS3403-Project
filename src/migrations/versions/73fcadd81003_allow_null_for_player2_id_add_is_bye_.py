"""Allow null for player2_id, add is_bye flag and not started statuses

Revision ID: 73fcadd81003
Revises: 6315bf773ac3
Create Date: 2025-05-10 14:35:39.322779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73fcadd81003'
down_revision = '6315bf773ac3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_bye', sa.Boolean(), nullable=True))
        batch_op.alter_column('player2_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.drop_constraint('match_status_check', type_='check'),
        batch_op.create_check_constraint('match_status_check', "status IN ('not started', 'in progress', 'completed')"),

    with op.batch_alter_table('rounds', schema=None) as batch_op:
        batch_op.drop_constraint('round_status_check', type_='check'),
        batch_op.create_check_constraint('round_status_check', "status IN ('not started', 'in progress', 'completed')")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('player2_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('is_bye'),
        batch_op.drop_constraint('match_status_check', type_='check'),
        batch_op.create_check_constraint('match_status_check', "status IN ('not started', 'in progress', 'completed')"),

    with op.batch_alter_table('rounds', schema=None) as batch_op:
        batch_op.drop_constraint('round_status_check', type_='check'),
        batch_op.create_check_constraint('round_status_check', "status IN ('not started', 'in progress', 'completed')")

    # ### end Alembic commands ###
