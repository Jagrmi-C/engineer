"""create user_google table

Revision ID: dfc4ce13e1b6
Revises: 
Create Date: 2017-12-29 02:14:19.391009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfc4ce13e1b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_google',
        sa.Column('google_id', sa.String(50), primary_key=True),
        sa.Column('google_user', sa.String(50), nullable=False),
        sa.Column('google_email', sa.String(50), nullable=False)
    )


def downgrade():
    op.drop_table('user_google')
