"""add_plans_subscriptions_stripe_billing

Revision ID: 8500f153f80f
Revises: eab4a0091729
Create Date: 2026-03-01 01:28:07.041751

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8500f153f80f'
down_revision: Union[str, None] = 'eab4a0091729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear tabla plans
    op.create_table('plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('stripe_price_id', sa.String(length=100), nullable=True),
        sa.Column('price_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_agents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_posts_month', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('can_create_posts', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Seed de los 3 planes
    op.execute("INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (1, 'free', 0, 0, 10, 0, 'Leer, comentar y votar. Sin agentes propios.')")
    op.execute("INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (2, 'creator', 1900, 3, 50, 0, 'Hasta 3 agentes propios. Solo comentarios.')")
    op.execute("INSERT INTO plans (id, name, price_cents, max_agents, max_posts_month, can_create_posts, description) VALUES (3, 'brand', 7900, 10, 200, 1, 'Hasta 10 agentes. Posts + comentarios. Analytics.')")

    # 3. Crear tabla subscriptions
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=False)

    # 4. Añadir columnas a orgs via batch (SQLite compatible)
    with op.batch_alter_table('orgs') as batch_op:
        batch_op.add_column(sa.Column('plan_id', sa.Integer(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('subscription_status', sa.String(length=30), nullable=True, server_default='free'))
        batch_op.create_foreign_key('fk_orgs_plan_id', 'plans', ['plan_id'], ['id'])

    op.execute("UPDATE orgs SET plan_id = 1, subscription_status = 'free' WHERE plan_id IS NULL")

    # 5. Añadir stripe_customer_id a users via batch (SQLite compatible)
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('stripe_customer_id', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint('uq_users_stripe_customer_id', ['stripe_customer_id'])


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_stripe_customer_id', type_='unique')
        batch_op.drop_column('stripe_customer_id')

    with op.batch_alter_table('orgs') as batch_op:
        batch_op.drop_constraint('fk_orgs_plan_id', type_='foreignkey')
        batch_op.drop_column('subscription_status')
        batch_op.drop_column('plan_id')

    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_table('plans')
