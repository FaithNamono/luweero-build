import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ContractStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    ESCROW_LOCKED = "ESCROW_LOCKED"


class OrderStatus(str, enum.Enum):
    AWAITING_FULFILLMENT = "AWAITING_FULFILLMENT"
    PAID_PROCESSING = "PAID_PROCESSING"


class PaymentType(str, enum.Enum):
    ESCROW_LOCK = "ESCROW_LOCK"
    STORE_PURCHASE = "STORE_PURCHASE"


class TransactionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(60), nullable=False)
    # Object key of the uploaded engineering blueprint inside the cloud bucket.
    blueprint_object_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Contract(Base):
    """Escrow track: one row per milestone contract."""

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engineer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    project_location: Mapped[str] = mapped_column(String(200), nullable=False)
    milestone_title: Mapped[str] = mapped_column(String(200), nullable=False)
    milestone_budget_ugx: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=ContractStatus.PENDING_PAYMENT.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Order(Base):
    """E-commerce track: a hardware material order."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Plain integer (no FK): contractors may be registered in the identity service, not yet in `users`.
    contractor_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    delivery_site_location: Mapped[str] = mapped_column(String(200), nullable=False)
    total_ugx: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=OrderStatus.AWAITING_FULFILLMENT.value, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", order_by="OrderItem.id"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_ugx: Mapped[int] = mapped_column(BigInteger, nullable=False)
    line_total_ugx: Mapped[int] = mapped_column(BigInteger, nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")


class PaymentTransaction(Base):
    """Ledger of every webhook received. The unique reference makes callbacks idempotent."""

    __tablename__ = "payment_transactions"
    __table_args__ = (UniqueConstraint("transaction_reference", name="uq_payment_transaction_reference"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_status: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
