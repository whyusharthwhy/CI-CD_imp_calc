"""empty message

Revision ID: 30882acdbbda
Revises: 
Create Date: 2022-10-27 18:55:37.117873

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '30882acdbbda'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('created_at', sa.DateTime(), default= datetime.utcnow))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_column('user', 'created_at')
    with op.batch_alter_table("user") as batch_op:
    	batch_op.drop_column('created_at')
    # ### end Alembic commands ###
