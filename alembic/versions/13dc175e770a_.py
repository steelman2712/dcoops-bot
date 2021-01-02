"""empty message

Revision ID: 13dc175e770a
Revises: 7a8c46d27526
Create Date: 2020-12-28 01:19:47.019338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13dc175e770a'
down_revision = '7a8c46d27526'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'files', ['alias', 'server'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'files', type_='unique')
    # ### end Alembic commands ###