from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserProfileOut
from app.services import storage, trust

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile/{user_id}", response_model=UserProfileOut)
def get_profile(user_id: int, db: Session = Depends(get_db)) -> UserProfileOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"User {user_id} not found")
    return UserProfileOut(
        user_id=user.id,
        name=user.name,
        role=user.role,
        is_identity_verified_by_laboremus=trust.is_identity_verified_by_laboremus(user.id),
        is_credentials_verified_by_verify_ug=trust.is_credentials_verified_by_verify_ug(user.id),
        cloud_storage_blueprint_url=storage.build_blueprint_url(user.blueprint_object_key),
    )
