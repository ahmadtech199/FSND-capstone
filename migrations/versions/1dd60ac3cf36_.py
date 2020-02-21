"""empty message

Revision ID: 1dd60ac3cf36
Revises: 25cb50db8de8
Create Date: 2020-02-20 17:45:53.307661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dd60ac3cf36'
down_revision = '25cb50db8de8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('players', sa.Column('salary', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('players', 'salary')
    # ### end Alembic commands ###