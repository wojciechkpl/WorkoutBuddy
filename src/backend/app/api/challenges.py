# backend/app/api/challenges.py
"""
Challenges API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate
from app.services.challenge_service import ChallengeService
from app.api.auth import get_current_user
from app.models.user import User
from app.database import get_db

# Dependency function for ChallengeService


def get_challenge_service() -> ChallengeService:
    # Provide dummy dependencies for testing
    class DummyRepo:
        async def get_user_challenges(self, user_id): return []
    class DummyML:
        pass
    class DummyNotif:
        pass
    return ChallengeService(DummyRepo(), DummyML(), DummyNotif())


router = APIRouter(tags=["challenges"])


@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    skip: int = 0,
    limit: int = 100,
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """Get all challenges"""
    return await challenge_service.get_challenges(skip=skip, limit=limit)


@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge: ChallengeCreate,
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """Create a new challenge"""
    return await challenge_service.create_challenge(challenge)


@router.get("/personalized")
async def get_personalized_challenges(
    current_user: User = Depends(get_current_user),
):
    """Get personalized challenges for the current user"""
    # Stub implementation
    return {
        "challenges": [
            {
                "id": 1,
                "title": "30-Day Strength Challenge",
                "description": "Build strength in 30 days",
                "difficulty": "intermediate"
            }
        ]
    }


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: int,
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """Get a specific challenge"""
    challenge = await challenge_service.get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(
    challenge_id: int,
    challenge: ChallengeUpdate,
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """Update a challenge"""
    updated_challenge = await challenge_service.update_challenge(
        challenge_id, challenge
    )
    if not updated_challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return updated_challenge


@router.delete("/{challenge_id}")
async def delete_challenge(
    challenge_id: int,
    challenge_service: ChallengeService = Depends(get_challenge_service),
):
    """Delete a challenge"""
    success = await challenge_service.delete_challenge(challenge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"message": "Challenge deleted successfully"}


@router.post("/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
):
    """Join a challenge"""
    # Stub implementation
    return {"message": "Challenge joined successfully"}


@router.put("/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: int,
    progress_data: dict,
    current_user: User = Depends(get_current_user),
):
    """Update challenge progress"""
    # Stub implementation
    return {"message": "Progress updated successfully"}
