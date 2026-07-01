from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = 'c1108797b0d9'
down_revision: Union[str, Sequence[str], None] = '26b1ecb3730f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    op.add_column('audit_snapshots', sa.Column('summary_text', sa.Text(), nullable=True))
def downgrade() -> None:
    op.drop_column('audit_snapshots', 'summary_text')