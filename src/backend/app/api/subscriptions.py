from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/features")
def get_premium_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Get premium features"""
    return {"features": ["advanced analytics", "priority support", "exclusive content"]}


@router.post("/upgrade")
def upgrade_to_premium(
    upgrade_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Upgrade to premium subscription"""
    return {"message": "Upgraded to premium"}
