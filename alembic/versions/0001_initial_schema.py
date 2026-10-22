"""initial schema: users, contracts, orders, order_items, payment_transactions

Revision ID: 0001
Revises:
Create Date: 2026-10-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("role", sa.String(60), nullable=False),
        sa.Column("blueprint_object_key", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("engineer_name", sa.String(120), nullable=False),
        sa.Column("client_name", sa.String(200), nullable=False),
        sa.Column("project_location", sa.String(200), nullable=False),
        sa.Column("milestone_title", sa.String(200), nullable=False),
        sa.Column("milestone_budget_ugx", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contracts_status", "contracts", ["status"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contractor_id", sa.Integer(), nullable=False),
        sa.Column("delivery_site_location", sa.String(200), nullable=False),
        sa.Column("total_ugx", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_orders_contractor_id", "orders", ["contractor_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_ugx", sa.BigInteger(), nullable=False),
        sa.Column("line_total_ugx", sa.BigInteger(), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table(
        "payment_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_reference", sa.String(100), nullable=False),
        sa.Column("payment_type", sa.String(30), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=False),
        sa.Column("transaction_status", sa.String(20), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("transaction_reference", name="uq_payment_transaction_reference"),
    )


def downgrade() -> None:
    op.drop_table("payment_transactions")
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_contractor_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_contracts_status", table_name="contracts")
    op.drop_table("contracts")
    op.drop_table("users")
