"""second commit

Revision ID: a2866b1eb116
Revises: 2fb83365121c
Create Date: 2023-11-23 01:49:57.100320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2866b1eb116'
down_revision: Union[str, None] = '2fb83365121c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ASSESSMENT',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('unitCode', sa.String(length=10), nullable=True),
    sa.Column('assessmentName', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['unitCode'], ['UNIT.unitCode'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('HIGHLIGHT', sa.Column('studentId', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'HIGHLIGHT', 'USER', ['studentId'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'HIGHLIGHT', type_='foreignkey')
    op.drop_column('HIGHLIGHT', 'studentId')
    op.drop_table('ASSESSMENT')
    # ### end Alembic commands ###
