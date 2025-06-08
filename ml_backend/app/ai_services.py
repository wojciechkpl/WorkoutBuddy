import anthropic
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

from .core import models

logger = logging.getLogger(__name__)


class ChallengeResponse(BaseModel):
    title: str
    description: str
    duration: str
    difficulty: int
    equipment_needed: List[str]
    motivation_message: str
    ai_generated: bool = True


class CommunityMatchResponse(BaseModel):
    user_id: int
    name: str
    compatibility_score: float
    match_reasons: List[str]
    shared_interests: List[str]


class EncouragementResponse(BaseModel):
    message: str
    tone: str  # "encouraging", "motivational", "celebratory", "supportive"
    personalized: bool
    suggestions: List[str]


class AIService:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY", "dummy-key-for-testing")
        )
        self.enabled = bool(os.getenv("ANTHROPIC_API_KEY"))
        if not self.enabled:
            logger.warning(
                "Anthropic API key not found. AI features will use fallback responses."
            )

    async def generate_personalized_challenge(
        self,
        user: models.User,
        user_history: Dict[str, Any],
        preferences: Dict[str, Any] = None,
    ) -> ChallengeResponse:
        """Generate AI-powered personalized daily challenges"""

        if not self.enabled:
            return self._generate_fallback_challenge(user.goal_type)

        try:
            # Prepare user context for AI
            user_context = self._build_user_context(user, user_history, preferences)

            prompt = f"""Create a personalized fitness challenge for this user:

User Profile:
- Goal: {user.goal_type}
- Activity Level: {user.activity_level}
- Age: {datetime.now().year - user.year_of_birth}
- Recent Progress: {user_history.get("recent_completion_rate", "No data")}
- Preferred Equipment: {preferences.get("equipment", "Bodyweight") if preferences else "Bodyweight"}
- Time Available: {preferences.get("time_minutes", 15) if preferences else 15} minutes
- Previous Challenges: {user_history.get("recent_challenges", [])}

Create a challenge that:
1. Matches their fitness level and goals
2. Is achievable but progressive
3. Includes motivational messaging
4. Avoids repeating recent challenges

Return JSON with: title, description, duration, difficulty (1-5), equipment_needed (array), motivation_message"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse AI response
            content = response.content[0].text
            try:
                ai_data = json.loads(content)
                return ChallengeResponse(**ai_data)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._parse_text_response(content, user.goal_type)

        except Exception as e:
            logger.error(f"AI challenge generation failed: {e}")
            return self._generate_fallback_challenge(user.goal_type)

    async def analyze_community_compatibility(
        self,
        user: models.User,
        potential_matches: List[models.User],
        user_goals: List[models.Goal],
        match_goals: Dict[int, List[models.Goal]],
    ) -> List[CommunityMatchResponse]:
        """AI-powered community matching with detailed reasoning"""

        if not self.enabled:
            return self._generate_fallback_matches(potential_matches)

        try:
            matches = []

            for candidate in potential_matches[
                :5
            ]:  # Limit to top 5 for cost efficiency
                candidate_goals = match_goals.get(candidate.id, [])

                # Create compatibility analysis prompt
                prompt = f"""Analyze compatibility between two fitness community members:

User A (Seeking Match):
- Goals: {[g.title for g in user_goals]}
- Activity Level: {user.activity_level}
- Motivation Style: {getattr(user, "motivation_style", "Not specified")}
- Age: {datetime.now().year - user.year_of_birth}

User B (Potential Match):
- Goals: {[g.title for g in candidate_goals]}
- Activity Level: {candidate.activity_level}
- Motivation Style: {getattr(candidate, "motivation_style", "Not specified")}
- Age: {datetime.now().year - candidate.year_of_birth}

Provide compatibility analysis with:
1. Compatibility score (0-100)
2. 3 specific reasons why they'd be good matches
3. Shared interests/goals
4. Potential challenges

Return JSON with: compatibility_score, match_reasons (array), shared_interests (array)"""

                response = await self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                try:
                    ai_data = json.loads(response.content[0].text)
                    matches.append(
                        CommunityMatchResponse(
                            user_id=candidate.id,
                            name=f"{candidate.first_name} {candidate.last_name}"
                            if candidate.first_name
                            else f"User {candidate.id}",
                            compatibility_score=ai_data.get("compatibility_score", 0)
                            / 100.0,
                            match_reasons=ai_data.get("match_reasons", []),
                            shared_interests=ai_data.get("shared_interests", []),
                        )
                    )
                except json.JSONDecodeError:
                    # Fallback to basic compatibility
                    matches.append(self._calculate_basic_compatibility(user, candidate))

            # Sort by compatibility score
            matches.sort(key=lambda x: x.compatibility_score, reverse=True)
            return matches

        except Exception as e:
            logger.error(f"AI community matching failed: {e}")
            return self._generate_fallback_matches(potential_matches)

    async def generate_encouragement(
        self, user: models.User, context: Dict[str, Any]
    ) -> EncouragementResponse:
        """Generate personalized encouragement based on user progress and sentiment"""

        if not self.enabled:
            return self._generate_fallback_encouragement(context)

        try:
            prompt = f"""Generate personalized encouragement for a fitness community member:

User Context:
- Recent Check-in: {context.get("recent_checkin", "No recent activity")}
- Progress Trend: {context.get("progress_trend", "Unknown")}
- Goal: {user.goal_type}
- Engagement Level: {context.get("engagement_level", "Medium")}
- Time Since Last Activity: {context.get("days_since_last", 0)} days
- Recent Challenges: {context.get("recent_challenges_completed", 0)}

Generate encouragement that:
1. Acknowledges their current situation
2. Provides specific, actionable motivation
3. Matches their goal and activity level
4. Suggests next steps

Return JSON with: message, tone (encouraging/motivational/celebratory/supportive), suggestions (array of 2-3 specific actions)"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}],
            )

            try:
                ai_data = json.loads(response.content[0].text)
                return EncouragementResponse(**ai_data, personalized=True)
            except json.JSONDecodeError:
                return EncouragementResponse(
                    message=response.content[0].text.strip(),
                    tone="encouraging",
                    personalized=True,
                    suggestions=[
                        "Keep up the great work!",
                        "Try a new challenge today!",
                    ],
                )

        except Exception as e:
            logger.error(f"AI encouragement generation failed: {e}")
            return self._generate_fallback_encouragement(context)

    def _build_user_context(
        self, user: models.User, history: Dict, preferences: Dict = None
    ) -> Dict:
        """Build comprehensive user context for AI"""
        return {
            "user_id": user.id,
            "goal_type": user.goal_type,
            "activity_level": user.activity_level,
            "age": datetime.now().year - user.year_of_birth,
            "engagement_score": getattr(user, "community_engagement_score", 0),
            "history": history,
            "preferences": preferences or {},
        }

    def _generate_fallback_challenge(self, goal_type: str) -> ChallengeResponse:
        """Fallback challenges when AI is unavailable"""
        challenges = {
            "cardio": ChallengeResponse(
                title="Quick Cardio Burst",
                description="5 minutes of alternating: 30 seconds jumping jacks, 30 seconds rest. Repeat 5 times.",
                duration="5 minutes",
                difficulty=3,
                equipment_needed=[],
                motivation_message="Every step counts! You've got this! 💪",
                ai_generated=False,
            ),
            "strength": ChallengeResponse(
                title="Bodyweight Power",
                description="3 rounds: 8 push-ups, 12 squats, 15-second plank. Rest 1 minute between rounds.",
                duration="10 minutes",
                difficulty=4,
                equipment_needed=[],
                motivation_message="Build that strength one rep at a time! 🔥",
                ai_generated=False,
            ),
            "flexibility": ChallengeResponse(
                title="Morning Mobility",
                description="Gentle flow: neck rolls, shoulder circles, hip circles, calf raises. Hold each for 30 seconds.",
                duration="8 minutes",
                difficulty=2,
                equipment_needed=[],
                motivation_message="Your body will thank you for this care! 🧘‍♀️",
                ai_generated=False,
            ),
        }

        return challenges.get(goal_type, challenges["cardio"])

    def _generate_fallback_matches(
        self, users: List[models.User]
    ) -> List[CommunityMatchResponse]:
        """Basic compatibility matching when AI is unavailable"""
        matches = []
        for i, user in enumerate(users[:3]):
            matches.append(
                CommunityMatchResponse(
                    user_id=user.id,
                    name=f"{user.first_name} {user.last_name}"
                    if user.first_name
                    else f"User {user.id}",
                    compatibility_score=0.8 - (i * 0.1),  # Decreasing scores
                    match_reasons=[
                        "Similar fitness goals",
                        "Compatible activity levels",
                        "Active community member",
                    ],
                    shared_interests=["fitness", "wellness"],
                )
            )
        return matches

    def _generate_fallback_encouragement(self, context: Dict) -> EncouragementResponse:
        """Fallback encouragement when AI is unavailable"""
        messages = [
            "You're doing great! Keep pushing towards your goals! 🌟",
            "Every workout counts! You're building something amazing! 💪",
            "Progress isn't always linear, but you're moving forward! 🚀",
            "Your consistency is inspiring! Keep it up! ✨",
        ]

        import random

        return EncouragementResponse(
            message=random.choice(messages),
            tone="encouraging",
            personalized=False,
            suggestions=[
                "Try a new workout today",
                "Connect with your accountability partner",
                "Set a small goal for tomorrow",
            ],
        )

    def _parse_text_response(self, content: str, goal_type: str) -> ChallengeResponse:
        """Parse AI response when JSON parsing fails"""
        # Basic parsing for non-JSON responses
        return ChallengeResponse(
            title=f"AI Challenge for {goal_type.title()}",
            description=content[:200] + "..." if len(content) > 200 else content,
            duration="15 minutes",
            difficulty=3,
            equipment_needed=[],
            motivation_message="AI-powered challenge just for you!",
            ai_generated=True,
        )

    def _calculate_basic_compatibility(
        self, user1: models.User, user2: models.User
    ) -> CommunityMatchResponse:
        """Basic compatibility calculation"""
        score = 0.5
        reasons = []

        if user1.goal_type == user2.goal_type:
            score += 0.3
            reasons.append(f"Both focused on {user1.goal_type} goals")

        if user1.activity_level == user2.activity_level:
            score += 0.2
            reasons.append("Similar activity levels")

        age_diff = abs(
            (datetime.now().year - user1.year_of_birth)
            - (datetime.now().year - user2.year_of_birth)
        )
        if age_diff < 10:
            score += 0.1
            reasons.append("Similar age groups")

        return CommunityMatchResponse(
            user_id=user2.id,
            name=f"{user2.first_name} {user2.last_name}"
            if user2.first_name
            else f"User {user2.id}",
            compatibility_score=min(score, 1.0),
            match_reasons=reasons or ["Active community member"],
            shared_interests=[user1.goal_type]
            if user1.goal_type == user2.goal_type
            else ["fitness"],
        )


# Global AI service instance
ai_service = AIService()
