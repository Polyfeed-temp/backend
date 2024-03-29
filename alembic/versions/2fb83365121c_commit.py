"""commit

Revision ID: 2fb83365121c
Revises: 
Create Date: 2023-11-23 00:41:12.293922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fb83365121c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UNIT',
    sa.Column('unitCode', sa.String(length=10), nullable=False),
    sa.Column('unitName', sa.String(length=255), nullable=True),
    sa.Column('offering', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('unitCode')
    )
    op.create_table('USER',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('monashId', sa.String(length=10), nullable=True),
    sa.Column('monashObjectId', sa.String(length=255), nullable=True),
    sa.Column('authcate', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('lastName', sa.String(length=255), nullable=True),
    sa.Column('firstName', sa.String(length=255), nullable=True),
    sa.Column('role', sa.Enum('Student', 'Tutor', 'CE', 'Admin', name='role'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('HIGHLIGHT',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('startMeta', sa.JSON(), nullable=True),
    sa.Column('endMeta', sa.JSON(), nullable=True),
    sa.Column('text', sa.String(length=255), nullable=True),
    sa.Column('url', sa.String(length=255), nullable=True),
    sa.Column('annotationTag', sa.Enum('Strength', 'Weakness', 'ActionItem', 'Confused', 'Other', name='annotationtag'), nullable=True),
    sa.Column('notes', sa.String(length=255), nullable=True),
    sa.Column('unitCode', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['unitCode'], ['UNIT.unitCode'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('STUDENT_UNIT',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('unitCode', sa.String(length=10), nullable=True),
    sa.Column('studentId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['studentId'], ['USER.id'], ),
    sa.ForeignKeyConstraint(['unitCode'], ['UNIT.unitCode'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ACTION',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=True),
    sa.Column('actionPoint', sa.Enum('FurtherPractice', 'ContactTutor', 'ReferLearningResources', name='actionpointcategory'), nullable=True),
    sa.Column('deadline', sa.Date(), nullable=True),
    sa.Column('annotationId', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['annotationId'], ['HIGHLIGHT.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ACTION')
    op.drop_table('STUDENT_UNIT')
    op.drop_table('HIGHLIGHT')
    op.drop_table('USER')
    op.drop_table('UNIT')
    # ### end Alembic commands ###
