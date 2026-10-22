from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contract, ContractStatus
from app.schemas import ContractCreate, ContractOut

router = APIRouter(prefix="/contracts", tags=["escrow"])


@router.post("/create", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)) -> Contract:
    """Create a milestone escrow contract. Location must contain "Luweero" (validated in the schema)."""
    contract = Contract(
        engineer_name=payload.engineer_name,
        client_name=payload.client_name,
        project_location=payload.project_location,
        milestone_title=payload.milestone_title,
        milestone_budget_ugx=payload.milestone_budget_ugx,
        status=ContractStatus.PENDING_PAYMENT.value,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract
