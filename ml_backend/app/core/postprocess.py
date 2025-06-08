"""
Data Postprocessing Module for WorkoutBuddy ML Backend

This module handles all output formatting and postprocessing
after ML model inference to create user-friendly responses.
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta


class OutputFormatter:
    """
    Main postprocessing class for transforming ML model outputs
    into structured, user-friendly responses.
    """

    def __init__(self):
        self.response_templates = self._load_response_templates()

    def format_workout_plan(
        self, ml_output: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format ML model output into a structured workout plan.

        Args:
            ml_output: Raw output from ML model
            user_data: User context data

        Returns:
            Formatted workout plan response
        """
        formatted_plan = {
            "user_id": user_data.get("id"),
            "plan_id": self._generate_plan_id(),
            "created_at": datetime.now().isoformat(),
            "title": self._generate_plan_title(ml_output, user_data),
            "description": self._generate_plan_description(ml_output, user_data),
            "duration_weeks": ml_output.get("duration_weeks", 4),
            "difficulty_level": ml_output.get("difficulty_level", "intermediate"),
            "weekly_schedule": self._format_weekly_schedule(ml_output),
            "exercises": self._format_exercises(ml_output.get("exercises", [])),
            "progression": self._format_progression_plan(ml_output),
            "estimated_calories_per_session": ml_output.get("estimated_calories", 300),
            "equipment_needed": ml_output.get("equipment_needed", ["bodyweight"]),
            "tips": self._generate_workout_tips(ml_output, user_data),
        }

        return formatted_plan

    def format_community_matches(
        self, ml_output: List[Dict], user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format ML community matching output into user-friendly profiles.

        Args:
            ml_output: Raw similarity scores and user matches
            user_data: Current user context

        Returns:
            List of formatted community match profiles
        """
        formatted_matches = []

        for match in ml_output:
            formatted_match = {
                "user_id": match.get("user_id"),
                "compatibility_score": round(match.get("similarity_score", 0) * 100, 1),
                "match_reasons": self._generate_match_reasons(match, user_data),
                "shared_interests": match.get("shared_interests", []),
                "workout_compatibility": {
                    "schedule_overlap": match.get("schedule_compatibility", 0),
                    "fitness_level_match": match.get("fitness_level_similarity", 0),
                    "goal_alignment": match.get("goal_similarity", 0),
                },
                "profile_summary": {
                    "fitness_level": match.get("activity_level", "intermediate"),
                    "primary_goals": match.get("primary_goals", []),
                    "preferred_workout_times": match.get("preferred_times", []),
                    "workout_frequency": match.get(
                        "workout_frequency", "3-4 times/week"
                    ),
                },
                "connection_potential": self._calculate_connection_potential(match),
            }
            formatted_matches.append(formatted_match)

        return sorted(
            formatted_matches, key=lambda x: x["compatibility_score"], reverse=True
        )

    def format_exercise_recommendations(
        self, ml_output: List[Dict], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format exercise recommendation output into detailed exercise cards.

        Args:
            ml_output: Raw exercise recommendations with scores
            user_context: User preferences and constraints

        Returns:
            List of formatted exercise recommendations
        """
        formatted_exercises = []

        for exercise in ml_output:
            formatted_exercise = {
                "exercise_id": exercise.get("id"),
                "name": exercise.get("name"),
                "description": exercise.get("description"),
                "recommendation_score": round(exercise.get("score", 0) * 100, 1),
                "recommendation_reason": self._generate_recommendation_reason(
                    exercise, user_context
                ),
                "muscle_groups": {
                    "primary": exercise.get("main_muscle_group"),
                    "secondary": exercise.get("secondary_muscles", []),
                },
                "difficulty": {
                    "level": exercise.get("difficulty"),
                    "beginner_friendly": exercise.get("difficulty")
                    in ["easy", "beginner"],
                },
                "equipment": {
                    "required": exercise.get("equipment", "bodyweight"),
                    "alternatives": exercise.get("equipment_alternatives", []),
                },
                "instructions": {
                    "setup": exercise.get("setup_instructions", ""),
                    "execution": exercise.get("execution_steps", []),
                    "tips": exercise.get("form_tips", []),
                },
                "suggested_sets_reps": self._generate_sets_reps_suggestion(
                    exercise, user_context
                ),
                "estimated_duration": exercise.get("estimated_duration_minutes", 2),
                "calories_per_rep": exercise.get("calories_per_rep", 0.5),
                "safety_notes": exercise.get("safety_notes", []),
                "progressions": {
                    "easier_variant": exercise.get("easier_variant"),
                    "harder_variant": exercise.get("harder_variant"),
                },
            }
            formatted_exercises.append(formatted_exercise)

        return formatted_exercises

    def format_progress_analysis(
        self, ml_output: Dict[str, Any], user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format progress analysis output into insights and recommendations.

        Args:
            ml_output: Progress analysis results
            user_data: User historical data

        Returns:
            Formatted progress analysis
        """
        return {
            "user_id": user_data.get("id"),
            "analysis_date": datetime.now().isoformat(),
            "overall_progress_score": round(ml_output.get("overall_score", 0) * 100, 1),
            "progress_trends": {
                "strength_trend": ml_output.get("strength_trend", "stable"),
                "consistency_trend": ml_output.get("consistency_trend", "stable"),
                "goal_progress": ml_output.get("goal_progress_percent", 0),
            },
            "achievements": self._format_achievements(
                ml_output.get("achievements", [])
            ),
            "areas_for_improvement": ml_output.get("improvement_areas", []),
            "next_milestones": self._format_next_milestones(ml_output),
            "personalized_insights": self._generate_progress_insights(
                ml_output, user_data
            ),
            "recommended_adjustments": ml_output.get("recommended_adjustments", []),
        }

    def _generate_plan_id(self) -> str:
        """Generate unique plan identifier."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"plan_{timestamp}"

    def _generate_plan_title(self, ml_output: Dict, user_data: Dict) -> str:
        """Generate personalized workout plan title."""
        goal = user_data.get("primary_goal", "fitness")
        level = ml_output.get("difficulty_level", "intermediate")
        duration = ml_output.get("duration_weeks", 4)

        titles = {
            "weight_loss": f"{duration}-Week Fat Burning {level.title()} Plan",
            "muscle_gain": f"{duration}-Week Muscle Building {level.title()} Program",
            "strength": f"{duration}-Week Strength Training {level.title()} Plan",
            "endurance": f"{duration}-Week Endurance {level.title()} Program",
            "general_fitness": f"{duration}-Week Complete Fitness {level.title()} Plan",
        }

        return titles.get(goal, f"{duration}-Week Personalized {level.title()} Plan")

    def _generate_plan_description(self, ml_output: Dict, user_data: Dict) -> str:
        """Generate personalized plan description."""
        goal = user_data.get("primary_goal", "general fitness")
        level = user_data.get("activity_level", "intermediate")

        return (
            f"A personalized {goal} plan designed for {level} level. "
            f"This plan adapts to your schedule and preferences while "
            f"progressively challenging you to reach your goals."
        )

    def _format_weekly_schedule(self, ml_output: Dict) -> Dict[str, Any]:
        """Format weekly workout schedule."""
        schedule = ml_output.get("weekly_schedule", {})

        return {
            "workout_days": schedule.get("workout_days", 3),
            "rest_days": schedule.get("rest_days", 4),
            "recommended_schedule": schedule.get(
                "recommended_days", ["Monday", "Wednesday", "Friday"]
            ),
            "session_duration_minutes": schedule.get("session_duration", 45),
            "intensity_distribution": {
                "high": schedule.get("high_intensity_days", 1),
                "moderate": schedule.get("moderate_intensity_days", 2),
                "low": schedule.get("low_intensity_days", 0),
            },
        }

    def _format_exercises(self, exercises: List[Dict]) -> List[Dict[str, Any]]:
        """Format exercise list with detailed information."""
        formatted = []

        for exercise in exercises:
            formatted.append(
                {
                    "exercise_id": exercise.get("id"),
                    "name": exercise.get("name"),
                    "sets": exercise.get("sets", 3),
                    "reps": exercise.get("reps", "8-12"),
                    "rest_seconds": exercise.get("rest_seconds", 60),
                    "muscle_group": exercise.get("main_muscle_group"),
                    "equipment": exercise.get("equipment"),
                    "difficulty": exercise.get("difficulty"),
                    "notes": exercise.get("notes", ""),
                }
            )

        return formatted

    def _format_progression_plan(self, ml_output: Dict) -> Dict[str, Any]:
        """Format progression plan details."""
        progression = ml_output.get("progression", {})

        return {
            "progression_type": progression.get("type", "linear"),
            "weekly_increases": {
                "weight": progression.get("weight_increase_percent", 2.5),
                "reps": progression.get("rep_increase", 1),
                "duration": progression.get("duration_increase_minutes", 2),
            },
            "deload_week": progression.get("deload_week", 4),
            "progression_notes": progression.get("notes", []),
        }

    def _generate_workout_tips(self, ml_output: Dict, user_data: Dict) -> List[str]:
        """Generate personalized workout tips."""
        tips = [
            "Always warm up for 5-10 minutes before starting your workout",
            "Focus on proper form rather than lifting heavy weights",
            "Stay hydrated throughout your workout session",
        ]

        # Add personalized tips based on user data
        if user_data.get("activity_level") == "beginner":
            tips.append("Start with bodyweight exercises to build foundation strength")

        if user_data.get("primary_goal") == "weight_loss":
            tips.append(
                "Consider adding 10-15 minutes of cardio after strength training"
            )

        return tips

    def _generate_match_reasons(self, match: Dict, user_data: Dict) -> List[str]:
        """Generate reasons why users are compatible."""
        reasons = []

        if match.get("goal_similarity", 0) > 0.8:
            reasons.append("You share similar fitness goals")

        if match.get("schedule_compatibility", 0) > 0.7:
            reasons.append("Your workout schedules align well")

        if match.get("fitness_level_similarity", 0) > 0.8:
            reasons.append("You're at similar fitness levels")

        return reasons or ["Potential for good workout partnership"]

    def _calculate_connection_potential(self, match: Dict) -> str:
        """Calculate overall connection potential."""
        score = match.get("similarity_score", 0)

        if score > 0.8:
            return "high"
        elif score > 0.6:
            return "medium"
        else:
            return "low"

    def _generate_recommendation_reason(
        self, exercise: Dict, user_context: Dict
    ) -> str:
        """Generate reason for exercise recommendation."""
        reasons = []

        if exercise.get("score", 0) > 0.8:
            reasons.append("Highly recommended for your goals")

        if exercise.get("equipment") == "bodyweight":
            reasons.append("No equipment needed")

        if user_context.get("primary_goal") in exercise.get("benefits", []):
            reasons.append("Perfect for your fitness goals")

        return "; ".join(reasons) or "Good fit for your current routine"

    def _generate_sets_reps_suggestion(
        self, exercise: Dict, user_context: Dict
    ) -> Dict[str, Any]:
        """Generate sets and reps suggestion based on user level."""
        level = user_context.get("activity_level", "intermediate")
        goal = user_context.get("primary_goal", "general_fitness")

        suggestions = {
            "beginner": {"sets": 2, "reps": "8-10", "rest_seconds": 90},
            "intermediate": {"sets": 3, "reps": "8-12", "rest_seconds": 60},
            "advanced": {"sets": 4, "reps": "6-10", "rest_seconds": 45},
        }

        base_suggestion = suggestions.get(level, suggestions["intermediate"])

        # Adjust based on goal
        if goal == "strength":
            base_suggestion["reps"] = "3-6"
            base_suggestion["rest_seconds"] = 120
        elif goal == "endurance":
            base_suggestion["reps"] = "12-20"
            base_suggestion["rest_seconds"] = 30

        return base_suggestion

    def _format_achievements(self, achievements: List[Dict]) -> List[Dict[str, Any]]:
        """Format user achievements."""
        formatted = []

        for achievement in achievements:
            formatted.append(
                {
                    "title": achievement.get("title"),
                    "description": achievement.get("description"),
                    "date_earned": achievement.get("date"),
                    "category": achievement.get("category", "general"),
                    "points": achievement.get("points", 0),
                }
            )

        return formatted

    def _format_next_milestones(self, ml_output: Dict) -> List[Dict[str, Any]]:
        """Format upcoming milestones."""
        milestones = ml_output.get("next_milestones", [])

        return [
            {
                "title": milestone.get("title"),
                "target_date": milestone.get("target_date"),
                "progress_required": milestone.get("progress_required"),
                "estimated_effort": milestone.get("estimated_effort"),
            }
            for milestone in milestones
        ]

    def _generate_progress_insights(
        self, ml_output: Dict, user_data: Dict
    ) -> List[str]:
        """Generate personalized progress insights."""
        insights = []

        consistency = ml_output.get("consistency_score", 0)
        if consistency > 0.8:
            insights.append("Your workout consistency is excellent! Keep it up.")
        elif consistency < 0.5:
            insights.append("Try to maintain more consistent workout schedule.")

        progress_rate = ml_output.get("progress_rate", 0)
        if progress_rate > 0.1:
            insights.append("You're making great progress towards your goals.")

        return insights

    def _load_response_templates(self) -> Dict[str, str]:
        """Load response templates for consistent formatting."""
        return {
            "success": "Operation completed successfully",
            "error": "An error occurred while processing your request",
            "no_data": "No data available for this request",
        }
