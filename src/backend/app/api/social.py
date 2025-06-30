# backend/app/api/social.py
"""
Social features API endpoints
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.friendship import Friendship
from app.models.user import User
from app.schemas.user import UserResponse
from app.models.safety import UserBlock, UserReport
from app.models.friend_invitation import FriendInvitation

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


# Friend Invitation System Endpoints
@router.post("/invitations/send")
async def send_friend_invitation(
    invitation_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a friend invitation via email or SMS"""
    invitation_type = invitation_data.get("invitation_type", "email")
    personalized_message = invitation_data.get("personalized_message", "")
    invitee_email = invitation_data.get("invitee_email")
    invitee_phone = invitation_data.get("invitee_phone")

    if invitation_type == "email":
        if not invitee_email:
            raise HTTPException(
                status_code=400,
                detail="invitee_email is required for email invitations",
            )
    elif invitation_type == "sms":
        if not invitee_phone:
            raise HTTPException(
                status_code=400, detail="invitee_phone is required for SMS invitations"
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid invitation_type")

    # Generate invitation code
    invitation_code = f"inv_{current_user.id}_{int(datetime.utcnow().timestamp())}"
    status_value = "pending"
    # Create invitation record
    invitation = FriendInvitation(
        inviter_id=current_user.id,
        invitee_email=invitee_email if invitation_type == "email" else None,
        invitee_phone=invitee_phone if invitation_type == "sms" else None,
        invitation_code=invitation_code,
        invitation_type=invitation_type,
        personalized_message=personalized_message,
        status=status_value,
        created_at=datetime.utcnow(),
    )
    db.add(invitation)
    db.commit()
    return {
        "message": "Invitation sent",
        "invitation_code": invitation_code,
        "status": status_value,
        "invitation_type": invitation_type,
    }


@router.post("/invitations/accept/{invitation_code}")
async def accept_friend_invitation(
    invitation_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a friend invitation"""
    # Find the invitation
    invitation = (
        db.query(FriendInvitation)
        .filter(
            FriendInvitation.invitation_code == invitation_code,
            FriendInvitation.status == "pending",
        )
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=404, detail="Invitation not found or already used"
        )

    # Create friendship
    friendship = Friendship(
        user_id=invitation.inviter_id,
        friend_id=current_user.id,
        status="accepted",
        is_accepted=True,
        accepted_at=datetime.utcnow(),
    )

    # Update invitation status
    invitation.status = "accepted"
    invitation.accepted_user_id = current_user.id
    invitation.accepted_at = datetime.utcnow()

    db.add(friendship)
    db.commit()

    return {"status": "accepted"}


@router.get("/invitations/status")
async def get_invitation_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invitation status dashboard"""
    # Stub implementation
    return {
        "invitations": [],
        "analytics": {"total_sent": 0, "total_accepted": 0, "acceptance_rate": 0.0},
    }


@router.post("/invitations/import-contacts")
async def import_contacts(
    contacts_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Import contacts and find existing users"""
    # Stub implementation
    return {
        "existing_users": [],
        "new_invitations": len(contacts_data.get("contacts", [])),
    }


# Community Management Endpoints
@router.post("/communities/")
async def create_community(
    community_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new community"""
    # Stub implementation
    return {
        "id": 1,
        "name": community_data.get("name", "Test Community"),
        "description": community_data.get("description", ""),
        "created_by": current_user.id,
        "category": community_data.get("category", "strength"),
        "privacy_level": community_data.get("privacy_level", "public"),
    }


@router.post("/communities/{community_id}/join")
async def join_community(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join a community"""
    # Stub implementation
    return {"status": "joined"}


@router.get("/communities/recommendations")
async def get_community_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get personalized community recommendations"""
    # Stub implementation
    return {
        "recommendations": [
            {
                "id": 1,
                "name": "Strength Training Community",
                "description": "For strength enthusiasts",
                "match_score": 0.85,
            }
        ]
    }


@router.get("/communities/matching")
async def community_matching_algorithm(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get community matching algorithm results"""
    # Stub implementation
    return {
        "matches": [
            {"community_id": 1, "match_score": 0.85, "reason": "Similar fitness goals"}
        ]
    }


# Privacy Controls Endpoints
@router.post("/privacy/controls")
async def set_privacy_controls(
    privacy_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set privacy controls"""
    # Stub implementation
    return {"message": "Privacy controls updated successfully"}


@router.get("/privacy/controls")
async def get_privacy_controls(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get privacy controls"""
    # Stub implementation
    return {
        "profile_visibility": "public",
        "workout_visibility": "friends_only",
        "stats_visibility": "private",
    }


@router.post("/privacy/account-type")
async def account_type_management(
    account_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manage account type (public/private)"""
    # Stub implementation
    return {"message": "Account type updated successfully"}


# Safety and Moderation Endpoints
@router.post("/safety/block")
async def block_user(
    block_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Block a user"""
    blocked_user_id = block_data.get("blocked_user_id")
    block_reason = block_data.get("block_reason", "No reason provided")

    # Check if user exists
    blocked_user = db.query(User).filter(User.id == blocked_user_id).first()
    if not blocked_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already blocked
    existing_block = (
        db.query(UserBlock)
        .filter(
            UserBlock.blocker_id == current_user.id,
            UserBlock.blocked_id == blocked_user_id,
        )
        .first()
    )

    if existing_block:
        return {"message": "User already blocked"}

    # Create block record
    user_block = UserBlock(
        blocker_id=current_user.id,
        blocked_id=blocked_user_id,
        block_reason=block_reason,
        block_type=block_data.get("block_type", "user"),
    )

    db.add(user_block)
    db.flush()
    db.commit()
    db.refresh(user_block)
    return {"message": "User blocked successfully"}


@router.post("/safety/report")
async def report_content(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Report content or user"""
    # Stub implementation
    return {"message": "Report submitted successfully"}


@router.get("/safety/status")
async def get_safety_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get safety status including blocked users"""
    # Get blocked users
    blocked_users = (
        db.query(User)
        .join(UserBlock)
        .filter(UserBlock.blocker_id == current_user.id)
        .all()
    )

    # Get reports made by user
    user_reports = (
        db.query(UserReport).filter(UserReport.reporter_id == current_user.id).all()
    )

    return {
        "blocked_users": [
            {"user_id": user.id, "username": user.username, "email": user.email}
            for user in blocked_users
        ],
        "reports_made": len(user_reports),
        "safety_score": 95.0,  # Stub value
    }


# Challenge System Endpoints
@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join a challenge"""
    # Stub implementation
    return {"message": "Challenge joined successfully"}


@router.put("/challenges/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: int,
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update challenge progress"""
    # Stub implementation
    return {"message": "Progress updated successfully"}


# Premium Features Endpoints
@router.get("/premium/features")
async def get_premium_features(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get premium features"""
    # Stub implementation
    return {
        "features": ["Advanced Analytics", "Custom Workout Plans", "Priority Support"],
        "is_premium": False,
    }


@router.post("/premium/upgrade")
async def upgrade_to_premium(
    upgrade_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upgrade to premium"""
    # Stub implementation
    return {"message": "Upgraded to premium successfully"}
