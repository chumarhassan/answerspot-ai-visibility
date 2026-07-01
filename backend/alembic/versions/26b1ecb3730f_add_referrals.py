from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = '26b1ecb3730f'
down_revision: Union[str, Sequence[str], None] = 'd20ce6be4a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    conn = op.get_bind()
    columns = [c['name'] for c in sa.inspect(conn).get_columns('users')]
    if 'referral_code' not in columns:
        op.add_column('users', sa.Column('referral_code', sa.String(length=20), nullable=True))
    if 'referred_by_id' not in columns:
        op.add_column('users', sa.Column('referred_by_id', sa.Integer(), nullable=True))
    with op.batch_alter_table('users', schema=None) as batch_op:
        indexes = [i['name'] for i in sa.inspect(conn).get_indexes('users')]
        if 'ix_users_referral_code' not in indexes:
             batch_op.create_index(batch_op.f('ix_users_referral_code'), ['referral_code'], unique=True)
        batch_op.create_foreign_key('fk_user_referred_by', 'users', ['referred_by_id'], ['id'])
def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_referred_by', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_users_referral_code'))
        batch_op.drop_column('referred_by_id')
        batch_op.drop_column('referral_code')