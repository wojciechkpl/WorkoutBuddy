"""
AI Services for WorkoutBuddy ML Service

This module provides AI-powered features including:
- Personalized challenge generation
- Community compatibility matching
- Personalized encouragement messages
"""

import os
import random
from typing import Optional

from pydantic import BaseModel


class ChallengeResponse(BaseModel):
    """Response model for AI-generated challenges"""

    title: str
    description: str
    duration: str
    difficulty: int
    equipment_needed: list[str]
    motivation_message: str
    ai_generated: bool


class CommunityMatchResponse(BaseModel):
    """Response model for community compatibility matches"""

    name: str
    compatibility_score: float
    match_reasons: list[str]
    shared_interests: list[str]


class EncouragementResponse(BaseModel):
    """Response model for personalized encouragement"""

    message: str
    tone: str
    personalized: bool
    suggestions: list[str]


class AIService:
    """AI service for WorkoutBuddy with fallback mechanisms"""

    def __init__(self):
        self.enabled = bool(os.getenv("ANTHROPIC_API_KEY"))
        if not self.enabled:
            print(
                "Anthropic API key not found. AI features will use fallback responses."
            )

    async def generate_personalized_challenge(
        self,
        user,
        user_history: Optional[dict] = None,
        preferences: Optional[dict] = None,
    ) -> ChallengeResponse:
        """Generate personalized workout challenge"""

        if not self.enabled:
            return self._get_fallback_challenge(user)

        # TODO: Implement actual AI challenge generation
        # For now, return fallback
        return self._get_fallback_challenge(user)

    async def analyze_community_compatibility(
        self, user, potential_matches: list, user_goals: list, match_goals: dict
    ) -> list[CommunityMatchResponse]:
        """Analyze compatibility between users"""

        if not self.enabled:
            return self._get_fallback_matches(user, potential_matches)

        # TODO: Implement actual AI compatibility analysis
        # For now, return fallback
        return self._get_fallback_matches(user, potential_matches)

    async def generate_encouragement(
        self, user, context: dict
    ) -> EncouragementResponse:
        """Generate personalized encouragement message"""

        if not self.enabled:
            return self._get_fallback_encouragement(context)

        # TODO: Implement actual AI encouragement generation
        # For now, return fallback
        return self._get_fallback_encouragement(context)

    def _get_fallback_challenge(self, user) -> ChallengeResponse:
        """Generate fallback challenge when AI is unavailable"""

        challenges = {
            "STRENGTH": {
                "title": "Bodyweight Power",
                "description": "3 rounds: 8 push-ups, 12 squats, 15-second plank. Rest 1 minute between rounds.",
                "duration": "10 minutes",
                "difficulty": 2,
                "equipment_needed": [],
                "motivation_message": "Build that strength one rep at a time! 🔥",
            },
            "ENDURANCE": {
                "title": "Quick Cardio Burst",
                "description": "5 minutes of alternating: 30 seconds jumping jacks, 30 seconds rest. Repeat 5 times.",
                "duration": "5 minutes",
                "difficulty": 3,
                "equipment_needed": [],
                "motivation_message": "Every step counts! You've got this! 💪",
            },
            "GENERAL_FITNESS": {
                "title": "Morning Mobility",
                "description": "Gentle flow: neck rolls, shoulder circles, hip circles, calf raises. Hold each for 30 seconds.",
                "duration": "8 minutes",
                "difficulty": 1,
                "equipment_needed": [],
                "motivation_message": "Your body will thank you for this care! 🧘‍♀️",
            },
            "MUSCLE_GAIN": {
                "title": "Strength Builder",
                "description": "4 rounds: 10 squats, 8 push-ups, 6 lunges per leg. Rest 90 seconds between rounds.",
                "duration": "15 minutes",
                "difficulty": 3,
                "equipment_needed": [],
                "motivation_message": "Muscle is built one rep at a time! 💪",
            },
        }

        goal = getattr(user, "fitness_goal", "GENERAL_FITNESS")
        challenge = challenges.get(goal, challenges["GENERAL_FITNESS"])

        return ChallengeResponse(
            title=challenge["title"],
            description=challenge["description"],
            duration=challenge["duration"],
            difficulty=challenge["difficulty"],
            equipment_needed=challenge["equipment_needed"],
            motivation_message=challenge["motivation_message"],
            ai_generated=False,
        )

    def _get_fallback_matches(
        self, user, potential_matches
    ) -> list[CommunityMatchResponse]:
        """Generate fallback community matches when AI is unavailable"""

        matches = []
        for i, match in enumerate(potential_matches[:3]):  # Limit to 3 matches
            compatibility = random.uniform(0.6, 0.9)
            matches.append(
                CommunityMatchResponse(
                    name=getattr(match, "full_name", f"User {match.id}"),
                    compatibility_score=compatibility,
                    match_reasons=[
                        "Similar fitness goals and experience level",
                        "Compatible workout schedules",
                        "Shared motivation style",
                    ],
                    shared_interests=["fitness", "health", "wellness"],
                )
            )

        return matches

    def _get_fallback_encouragement(self, context: dict) -> EncouragementResponse:
        """Generate fallback encouragement when AI is unavailable"""

        progress_trend = context.get("progress_trend", "stable")

        if progress_trend == "Improving":
            message = "You're on fire! Your consistency is paying off! 🔥"
            tone = "motivational"
            suggestions = ["Keep pushing your limits", "Try a new exercise today"]
        elif progress_trend == "Declining":
            message = "Every journey has ups and downs. You've got this! 💪"
            tone = "supportive"
            suggestions = ["Start with a short workout", "Remember why you started"]
        else:
            message = "Your consistency is inspiring! Keep it up! ✨"
            tone = "encouraging"
            suggestions = ["Try a new exercise today", "Set a small goal for this week"]

        return EncouragementResponse(
            message=message, tone=tone, personalized=False, suggestions=suggestions
        )


# Global AI service instance
ai_service = AIService()
