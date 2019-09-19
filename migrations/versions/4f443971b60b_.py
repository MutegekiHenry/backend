"""empty message

Revision ID: 4f443971b60b
Revises: 25c9d573c1b8
Create Date: 2019-09-15 23:03:01.896800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f443971b60b'
down_revision = '25c9d573c1b8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organisation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('organisation_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('orgainsation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['orgainsation_id'], ['organisation.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key(None, 'namespace', 'organisation', ['orgainsation_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'namespace', type_='foreignkey')
    op.drop_table('organisation_members')
    op.drop_table('organisation')
    # ### end Alembic commands ###
