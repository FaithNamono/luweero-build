from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem, OrderStatus
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/store", tags=["store"])


@router.post("/order", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(payload: OrderCreate, db: Session = Depends(get_db)) -> Order:
    """Place a hardware order; the cumulative total is computed server-side from the line items."""
    items = [
        OrderItem(
            product_id=i.product_id,
            product_name=i.product_name,
            quantity=i.quantity,
            unit_price_ugx=i.unit_price_ugx,
            line_total_ugx=i.quantity * i.unit_price_ugx,
        )
        for i in payload.items
    ]
    order = Order(
        contractor_id=payload.contractor_id,
        delivery_site_location=payload.delivery_site_location,
        total_ugx=sum(i.line_total_ugx for i in items),
        status=OrderStatus.AWAITING_FULFILLMENT.value,
        items=items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
