from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/partnerships")
def create_accountability_partnership(
    partnership_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Create accountability partnership"""
    return {"message": "Accountability partnership created"}


@router.get("/partners")
def get_accountability_partners(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Get accountability partners"""
    return {"partners": []}


@router.post("/checkins")
def create_accountability_checkin(
    checkin_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Create accountability check-in"""
    return {"message": "Accountability check-in created"}
