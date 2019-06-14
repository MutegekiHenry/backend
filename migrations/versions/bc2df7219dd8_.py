"""empty message

Revision ID: bc2df7219dd8
Revises: 042360d08ad7
Create Date: 2019-06-11 12:11:17.660807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bc2df7219dd8'
down_revision = '042360d08ad7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='admin_pkey')
    )
    # ### end Alembic commands ###