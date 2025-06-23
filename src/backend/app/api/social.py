# backend/app/api/social.py
"""
Social features API endpoints
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/friends/request/{username}")
async def send_friend_request(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a friend request to another user"""
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself",
        )

    # Find target user
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if friendship already exists
    existing_friendship = (
        db.query(Friendship)
        .filter(
            (
                (Friendship.user_id == current_user.id)
                & (Friendship.friend_id == target_user.id)
            )
            | (
                (Friendship.user_id == target_user.id)
                & (Friendship.friend_id == current_user.id)
            )
        )
        .first()
    )

    if existing_friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friendship request already exists",
        )

    # Create friendship request
    friendship = Friendship(
        user_id=current_user.id, friend_id=target_user.id, status="pending"
    )

    db.add(friendship)
    db.commit()

    logger.info(f"Friend request sent from {current_user.username} to {username}")
    return {"message": "Friend request sent successfully"}


@router.put("/friends/accept/{friendship_id}")
async def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a friend request"""
    friendship = (
        db.query(Friendship)
        .filter(
            Friendship.id == friendship_id,
            Friendship.friend_id == current_user.id,
            Friendship.status == "pending",
        )
        .first()
    )

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found"
        )

    friendship.status = "accepted"
    db.commit()

    logger.info(f"Friend request accepted by {current_user.username}")
    return {"message": "Friend request accepted"}


@router.put("/friends/reject/{friendship_id}")
async def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reject a friend request"""
    friendship = (
        db.query(Friendship)
        .filter(
            Friendship.id == friendship_id,
            Friendship.friend_id == current_user.id,
            Friendship.status == "pending",
        )
        .first()
    )

    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found"
        )

    db.delete(friendship)
    db.commit()

    logger.info(f"Friend request rejected by {current_user.username}")
    return {"message": "Friend request rejected"}


@router.get("/friends", response_model=list[UserResponse])
async def get_friends(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's friends"""
    friendships = (
        db.query(Friendship)
        .filter(
            (
                (Friendship.user_id == current_user.id)
                | (Friendship.friend_id == current_user.id)
            ),
            Friendship.status == "accepted",
        )
        .all()
    )

    friend_ids = []
    for friendship in friendships:
        if friendship.user_id == current_user.id:
            friend_ids.append(friendship.friend_id)
        else:
            friend_ids.append(friendship.user_id)

    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    return friends


@router.get("/friends/requests", response_model=list[UserResponse])
async def get_friend_requests(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get pending friend requests for current user"""
    pending_friendships = (
        db.query(Friendship)
        .filter(Friendship.friend_id == current_user.id, Friendship.status == "pending")
        .all()
    )

    requester_ids = [friendship.user_id for friendship in pending_friendships]
    requesters = db.query(User).filter(User.id.in_(requester_ids)).all()

    return requesters
