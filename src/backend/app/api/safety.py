from fastapi import APIRouter, Depends, HTTPException
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()

# In-memory store for blocked users: {user_id: set(blocked_user_ids)}
blocked_users_store = {}


@router.post("/block")
def block_user(
    block_data: dict,
    current_user: User = Depends(get_current_user),
):
    """Block a user"""
    blocked_user_id = block_data.get("blocked_user_id")
    if not blocked_user_id:
        raise HTTPException(status_code=400, detail="blocked_user_id is required")
    user_id = current_user.id
    if user_id not in blocked_users_store:
        blocked_users_store[user_id] = set()
    blocked_users_store[user_id].add(blocked_user_id)
    return {"message": "User blocked successfully"}


@router.post("/report")
def report_content(
    report_data: dict,
    current_user: User = Depends(get_current_user),
):
    """Report content or user"""
    # Stub implementation
    return {"message": "Report submitted successfully"}


@router.get("/status")
def get_safety_status(
    current_user: User = Depends(get_current_user),
):
    """Get safety status and settings"""
    user_id = current_user.id
    blocked = [{"user_id": uid} for uid in blocked_users_store.get(user_id, set())]
    return {"blocked_users": blocked, "reported_content": [], "safety_level": "normal"}
