from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
revision: str = 'd20ce6be4a26'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    op.create_table('processed_webhook_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.String(length=255), nullable=False),
    sa.Column('event_type', sa.String(length=120), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processed_webhook_events_event_id'), 'processed_webhook_events', ['event_id'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('oauth_provider', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('businesses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('category', sa.String(length=120), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('website', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_businesses_user_id'), 'businesses', ['user_id'], unique=False)
    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('plan', sa.Enum('free', 'starter', 'pro', name='plan'), nullable=False),
    sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
    sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('renewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=True)
    op.create_table('audit_snapshots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=True),
    sa.Column('platform', sa.Enum('gemini', 'chatgpt', 'perplexity', 'claude', name='platform'), nullable=False),
    sa.Column('query_text', sa.Text(), nullable=False),
    sa.Column('raw_response', sa.Text(), nullable=True),
    sa.Column('businesses_mentioned', sa.JSON(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'ok', 'failed', name='snapshotstatus'), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('ran_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_snapshots_business_id'), 'audit_snapshots', ['business_id'], unique=False)
    op.create_index(op.f('ix_audit_snapshots_ran_at'), 'audit_snapshots', ['ran_at'], unique=False)
    op.create_table('competitors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('competitor_name', sa.String(length=200), nullable=False),
    sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitors_business_id'), 'competitors', ['business_id'], unique=False)
    op.create_table('fix_recommendations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('business_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('review_volume', 'citation', 'schema', 'website', 'other', name='fixtype'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('open', 'done', name='fixstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fix_recommendations_business_id'), 'fix_recommendations', ['business_id'], unique=False)
def downgrade() -> None:
    op.drop_index(op.f('ix_fix_recommendations_business_id'), table_name='fix_recommendations')
    op.drop_table('fix_recommendations')
    op.drop_index(op.f('ix_competitors_business_id'), table_name='competitors')
    op.drop_table('competitors')
    op.drop_index(op.f('ix_audit_snapshots_ran_at'), table_name='audit_snapshots')
    op.drop_index(op.f('ix_audit_snapshots_business_id'), table_name='audit_snapshots')
    op.drop_table('audit_snapshots')
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_businesses_user_id'), table_name='businesses')
    op.drop_table('businesses')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_processed_webhook_events_event_id'), table_name='processed_webhook_events')
    op.drop_table('processed_webhook_events')