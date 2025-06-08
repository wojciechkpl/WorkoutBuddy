from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AccountabilityType(str, Enum):
    WORKOUT_PARTNER = "workout_partner"
    PROGRESS_CHECKER = "progress_checker"
    GOAL_SUPPORTER = "goal_supporter"
    COMMUNITY_GROUP = "community_group"


class CommunityConnectionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


# Goal Schemas
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    is_public: Optional[bool] = False
    wants_support: Optional[bool] = False


class GoalCreate(GoalBase):
    pass


class Goal(GoalBase):
    id: int
    owner_id: int
    success_probability: Optional[float] = 0.5
    community_support_count: Optional[int] = 0

    class Config:
        orm_mode = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: str
    year_of_birth: int
    height_ft: int
    height_in: int
    weight_lb: int
    height_cm: int
    weight_kg: int
    activity_level: str
    goal_type: str
    goal_date: datetime

    # Community accountability preferences
    wants_accountability_partner: Optional[bool] = False
    accountability_preference: Optional[AccountabilityType] = None
    motivation_style: Optional[str] = None
    time_zone: Optional[str] = None
    preferred_check_in_frequency: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    goals: List[Goal] = []
    retention_score: Optional[float] = 0.0
    community_engagement_score: Optional[float] = 0.0
    last_active: Optional[datetime] = None

    class Config:
        orm_mode = True


# Community Connection Schemas
class CommunityConnectionBase(BaseModel):
    connection_type: AccountabilityType
    goal_compatibility: Optional[float] = 0.0
    schedule_compatibility: Optional[float] = 0.0
    personality_compatibility: Optional[float] = 0.0


class CommunityConnectionCreate(CommunityConnectionBase):
    partner_id: int


class CommunityConnection(CommunityConnectionBase):
    id: int
    requester_id: int
    partner_id: int
    status: CommunityConnectionStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    total_check_ins: Optional[int] = 0
    mutual_success_rate: Optional[float] = 0.0
    partnership_satisfaction: Optional[float] = 0.0

    class Config:
        orm_mode = True


# Check-in Schemas
class AccountabilityCheckInBase(BaseModel):
    workout_completed: bool
    energy_level: Optional[int] = None
    motivation_level: Optional[int] = None
    notes: Optional[str] = None
    challenges_faced: Optional[str] = None


class AccountabilityCheckInCreate(AccountabilityCheckInBase):
    connection_id: int


class AccountabilityCheckIn(AccountabilityCheckInBase):
    id: int
    user_id: int
    connection_id: int
    check_in_date: datetime
    partner_responded: Optional[bool] = False
    partner_response: Optional[str] = None
    encouragement_sent: Optional[bool] = False
    response_time_hours: Optional[float] = None
    interaction_quality_score: Optional[float] = 0.0

    class Config:
        orm_mode = True


class PartnerResponseCreate(BaseModel):
    check_in_id: int
    response: str
    encouragement_sent: bool = True


# Goal Check-in Schemas
class GoalCheckInBase(BaseModel):
    progress_percentage: float
    is_on_track: bool = True
    confidence_level: Optional[int] = None
    notes: Optional[str] = None


class GoalCheckInCreate(GoalCheckInBase):
    goal_id: int


class GoalCheckIn(GoalCheckInBase):
    id: int
    goal_id: int
    user_id: int
    check_in_date: datetime
    community_views: Optional[int] = 0
    community_encouragement_count: Optional[int] = 0

    class Config:
        orm_mode = True


# Progress Update Schemas
class ProgressUpdateBase(BaseModel):
    update_text: str
    milestone_achieved: Optional[str] = None
    progress_percentage: float


class ProgressUpdateCreate(ProgressUpdateBase):
    goal_id: int


class ProgressUpdate(ProgressUpdateBase):
    id: int
    goal_id: int
    user_id: int
    created_at: datetime
    views_count: Optional[int] = 0
    encouragement_count: Optional[int] = 0
    shares_count: Optional[int] = 0

    class Config:
        orm_mode = True


# Feedback Schemas (Critical for hypothesis validation)
class UserFeedbackBase(BaseModel):
    community_impact_rating: Optional[int] = None
    accountability_effectiveness: Optional[int] = None
    motivation_improvement: Optional[int] = None
    adherence_improvement: Optional[int] = None
    most_helpful_feature: Optional[str] = None
    biggest_challenge: Optional[str] = None
    suggestions: Optional[str] = None
    would_recommend: Optional[bool] = None
    likelihood_to_continue: Optional[int] = None
    primary_retention_driver: Optional[str] = None


class UserFeedbackCreate(UserFeedbackBase):
    pass


class UserFeedback(UserFeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Community Group Schemas
class CommunityGroupBase(BaseModel):
    name: str
    description: str
    max_members: Optional[int] = 8
    requires_approval: Optional[bool] = True


class CommunityGroupCreate(CommunityGroupBase):
    pass


class CommunityGroup(CommunityGroupBase):
    id: int
    created_at: datetime
    is_active: Optional[bool] = True
    member_retention_rate: Optional[float] = 0.0
    average_goal_completion_rate: Optional[float] = 0.0
    average_engagement_score: Optional[float] = 0.0

    class Config:
        orm_mode = True


class GroupMembershipBase(BaseModel):
    role: Optional[str] = "member"


class GroupMembershipCreate(GroupMembershipBase):
    group_id: int


class GroupMembership(GroupMembershipBase):
    id: int
    user_id: int
    group_id: int
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    check_ins_count: Optional[int] = 0
    encouragements_given: Optional[int] = 0
    encouragements_received: Optional[int] = 0

    class Config:
        orm_mode = True


# Crawl Phase Analytics Schemas
class CommunityMetrics(BaseModel):
    """Key metrics for validating community accountability hypothesis"""

    total_users: int
    users_with_accountability_partners: int
    active_connections: int
    average_retention_score: float
    average_engagement_score: float
    goal_completion_rate_with_community: float
    goal_completion_rate_without_community: float
    community_impact_factor: float  # How much better community users perform


class PartnerRecommendation(BaseModel):
    """Recommended accountability partners for manual curation"""

    partner_user: User
    compatibility_score: float
    compatibility_reasons: List[str]
    shared_goals: List[str]
    schedule_overlap: str


# ML API Request/Response Schemas
class WorkoutPlanRequest(BaseModel):
    """Request schema for workout plan generation"""

    user_id: int
    duration_weeks: Optional[int] = 4
    workout_days_per_week: Optional[int] = 3
    session_duration_minutes: Optional[int] = 45
    equipment_available: Optional[List[str]] = ["bodyweight"]
    fitness_goals: Optional[List[str]] = ["general_fitness"]


class WorkoutPlanResponse(BaseModel):
    """Response schema for generated workout plans"""

    user_id: int
    plan_id: str
    created_at: str
    title: str
    description: str
    duration_weeks: int
    difficulty_level: str
    weekly_schedule: dict
    exercises: List[dict]
    progression: dict
    estimated_calories_per_session: int
    equipment_needed: List[str]
    tips: List[str]


class CommunityMatchRequest(BaseModel):
    """Request schema for community matching"""

    user_id: int
    max_matches: Optional[int] = 5
    location_radius_km: Optional[float] = 10.0
    compatibility_threshold: Optional[float] = 0.7


class CommunityMatchResponse(BaseModel):
    """Response schema for community matches"""

    user_id: int
    compatibility_score: float
    match_reasons: List[str]
    shared_interests: List[str]
    workout_compatibility: dict
    profile_summary: dict
    connection_potential: str


class ExerciseRecommendationRequest(BaseModel):
    """Request schema for exercise recommendations"""

    user_id: int
    muscle_groups: Optional[List[str]] = []
    equipment_available: Optional[List[str]] = ["bodyweight"]
    difficulty_level: Optional[str] = "intermediate"
    max_recommendations: Optional[int] = 10


class ExerciseRecommendation(BaseModel):
    """Response schema for exercise recommendations"""

    exercise_id: int
    name: str
    description: str
    recommendation_score: float
    recommendation_reason: str
    muscle_groups: dict
    difficulty: dict
    equipment: dict
    instructions: dict
    suggested_sets_reps: dict
    estimated_duration: int
    calories_per_rep: float
    safety_notes: List[str]
    progressions: dict
