import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import (
    Contract,
    ContractStatus,
    Order,
    OrderStatus,
    PaymentTransaction,
    PaymentType,
    TransactionStatus,
)
from app.schemas import WebhookPayload, WebhookResult

router = APIRouter(prefix="/mock-payment", tags=["payments"])


def _verify_secret(x_webhook_secret: str | None) -> None:
    expected = get_settings().webhook_shared_secret
    if not expected:
        return  # secret not configured (local dev): accept
    if not x_webhook_secret or not hmac.compare_digest(x_webhook_secret, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid webhook secret")


def _result(p: WebhookPayload, detail: str, new_status: str | None = None) -> WebhookResult:
    return WebhookResult(
        transaction_reference=p.transaction_reference,
        payment_type=p.payment_type.value,
        reference_id=p.reference_id,
        new_status=new_status,
        detail=detail,
    )


@router.post("/webhook", response_model=WebhookResult)
def payment_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db),
    x_webhook_secret: str | None = Header(default=None),
) -> WebhookResult:
    """Simulated Yo! Payments callback.

    - Idempotent: a repeated transaction_reference is acknowledged without re-applying anything.
    - Only SUCCESS callbacks change state; every callback is recorded in the payment ledger.
    """
    _verify_secret(x_webhook_secret)

    existing = db.scalar(
        select(PaymentTransaction).where(PaymentTransaction.transaction_reference == payload.transaction_reference)
    )
    if existing:
        return _result(payload, "Duplicate callback ignored (already processed)")

    if payload.payment_type == PaymentType.ESCROW_LOCK:
        target = db.get(Contract, payload.reference_id)
        label = "Contract"
        pending, done = ContractStatus.PENDING_PAYMENT.value, ContractStatus.ESCROW_LOCKED.value
    else:
        target = db.get(Order, payload.reference_id)
        label = "Order"
        pending, done = OrderStatus.AWAITING_FULFILLMENT.value, OrderStatus.PAID_PROCESSING.value

    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{label} {payload.reference_id} not found")

    ledger = PaymentTransaction(
        transaction_reference=payload.transaction_reference,
        payment_type=payload.payment_type.value,
        reference_id=payload.reference_id,
        transaction_status=payload.transaction_status.value,
        raw_payload=payload.model_dump(mode="json"),
    )

    detail = "Callback recorded; transaction was not successful, no state change"
    new_status = target.status

    if payload.transaction_status == TransactionStatus.SUCCESS:
        if target.status != pending:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"{label} {payload.reference_id} is '{target.status}', expected '{pending}'",
            )
        target.status = done
        new_status = done
        detail = f"{label} {payload.reference_id} moved to {done}"

    db.add(ledger)
    try:
        db.commit()
    except IntegrityError:  # concurrent duplicate callback won the race
        db.rollback()
        return _result(payload, "Duplicate callback ignored (already processed)")

    return _result(payload, detail, new_status)
