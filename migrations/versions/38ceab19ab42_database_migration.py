"""database migration.

Revision ID: 38ceab19ab42
Revises: 
Create Date: 2023-01-20 10:49:39.192683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38ceab19ab42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_password_changed', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_password_changed')

    # ### end Alembic commands ###
