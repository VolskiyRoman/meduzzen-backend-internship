"""fixed request fields

Revision ID: cff6b319b458
Revises: a34edb4583ae
Create Date: 2024-04-30 12:18:34.791694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cff6b319b458'
down_revision: Union[str, None] = 'a34edb4583ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_user_company_uc', 'company_members', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('_user_company_uc', 'company_members', ['user_id', 'company_id'])
    # ### end Alembic commands ###
