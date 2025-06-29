#!/usr/bin/env python3
"""
Enhanced Mock Data Population Script for WorkoutBuddy Social Features

This script populates the database with comprehensive mock data for testing
all the new social features described in the customer journey document.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "postgresql://workoutbuddy:workoutbuddy@localhost:5432/workoutbuddy"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class EnhancedMockDataPopulator:
    """Populates database with comprehensive mock data for social features testing"""

    def __init__(self):
        self.db = SessionLocal()
        self.users = []
        self.communities = []
        self.challenges = []
        self.friendships = []
        self.invitations = []
        self.partnerships = []
        self.subscriptions = []

    def create_enhanced_users(self):
        """Create users with enhanced social features"""
        
        # Enhanced user profiles with social features
        enhanced_users = [
            {
                "email": "sarah.johnson@workoutbuddy.test",
                "username": "sarah_fitness",
                "full_name": "Sarah Johnson",
                "age": 28,
                "fitness_goal": "strength",
                "experience_level": "intermediate",
                "account_type": "public",
                "discoverability_level": "all",
                "social_comfort_level": "high",
                "preferred_communication_style": "encouraging",
                "location_sharing_enabled": True,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "height": 165.0,
                "weight": 65.0,
                "unit_system": "METRIC"
            },
            {
                "email": "mike.chen@workoutbuddy.test",
                "username": "mike_runner",
                "full_name": "Mike Chen",
                "age": 32,
                "fitness_goal": "endurance",
                "experience_level": "advanced",
                "account_type": "public",
                "discoverability_level": "all",
                "social_comfort_level": "medium",
                "preferred_communication_style": "competitive",
                "location_sharing_enabled": True,
                "latitude": 40.7589,
                "longitude": -73.9851,
                "height": 178.0,
                "weight": 75.0,
                "unit_system": "METRIC"
            },
            {
                "email": "emma.wilson@workoutbuddy.test",
                "username": "emma_yoga",
                "full_name": "Emma Wilson",
                "age": 25,
                "fitness_goal": "wellness",
                "experience_level": "beginner",
                "account_type": "private",
                "discoverability_level": "friends_only",
                "social_comfort_level": "low",
                "preferred_communication_style": "supportive",
                "location_sharing_enabled": False,
                "latitude": 40.7505,
                "longitude": -73.9934,
                "height": 160.0,
                "weight": 55.0,
                "unit_system": "METRIC"
            },
            {
                "email": "david.kim@workoutbuddy.test",
                "username": "david_coach",
                "full_name": "David Kim",
                "age": 35,
                "fitness_goal": "strength",
                "experience_level": "advanced",
                "account_type": "public",
                "discoverability_level": "all",
                "social_comfort_level": "high",
                "preferred_communication_style": "mentoring",
                "location_sharing_enabled": True,
                "latitude": 40.7829,
                "longitude": -73.9654,
                "height": 182.0,
                "weight": 85.0,
                "unit_system": "IMPERIAL"
            },
            {
                "email": "lisa.garcia@workoutbuddy.test",
                "username": "lisa_warrior",
                "full_name": "Lisa Garcia",
                "age": 29,
                "fitness_goal": "strength",
                "experience_level": "intermediate",
                "account_type": "semi_private",
                "discoverability_level": "community_only",
                "social_comfort_level": "medium",
                "preferred_communication_style": "motivational",
                "location_sharing_enabled": True,
                "latitude": 40.7549,
                "longitude": -73.9840,
                "height": 168.0,
                "weight": 62.0,
                "unit_system": "METRIC"
            },
            {
                "email": "alex.patel@workoutbuddy.test",
                "username": "alex_hiit",
                "full_name": "Alex Patel",
                "age": 27,
                "fitness_goal": "endurance",
                "experience_level": "intermediate",
                "account_type": "public",
                "discoverability_level": "all",
                "social_comfort_level": "high",
                "preferred_communication_style": "energetic",
                "location_sharing_enabled": True,
                "latitude": 40.7614,
                "longitude": -73.9776,
                "height": 175.0,
                "weight": 70.0,
                "unit_system": "METRIC"
            },
            {
                "email": "nina.rodriguez@workoutbuddy.test",
                "username": "nina_zen",
                "full_name": "Nina Rodriguez",
                "age": 31,
                "fitness_goal": "wellness",
                "experience_level": "beginner",
                "account_type": "private",
                "discoverability_level": "friends_only",
                "social_comfort_level": "low",
                "preferred_communication_style": "gentle",
                "location_sharing_enabled": False,
                "latitude": 40.7484,
                "longitude": -73.9857,
                "height": 163.0,
                "weight": 58.0,
                "unit_system": "METRIC"
            },
            {
                "email": "james.thompson@workoutbuddy.test",
                "username": "james_lifter",
                "full_name": "James Thompson",
                "age": 33,
                "fitness_goal": "strength",
                "experience_level": "advanced",
                "account_type": "public",
                "discoverability_level": "all",
                "social_comfort_level": "high",
                "preferred_communication_style": "technical",
                "location_sharing_enabled": True,
                "latitude": 40.7589,
                "longitude": -73.9851,
                "height": 185.0,
                "weight": 90.0,
                "unit_system": "IMPERIAL"
            }
        ]

        for user_data in enhanced_users:
            # Check if user already exists
            existing_user = self.db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": user_data["email"]}
            ).fetchone()

            if existing_user:
                # Update existing user with new fields
                self.db.execute(
                    text("""
                        UPDATE users SET 
                            account_type = :account_type,
                            discoverability_level = :discoverability_level,
                            social_comfort_level = :social_comfort_level,
                            preferred_communication_style = :preferred_communication_style,
                            location_sharing_enabled = :location_sharing_enabled,
                            latitude = :latitude,
                            longitude = :longitude
                        WHERE email = :email
                    """),
                    user_data
                )
                user_id = existing_user[0]
            else:
                # Create new user
                result = self.db.execute(
                    text("""
                        INSERT INTO users (
                            email, username, full_name, age, fitness_goal, experience_level,
                            account_type, discoverability_level, social_comfort_level,
                            preferred_communication_style, location_sharing_enabled,
                            latitude, longitude, height, weight, unit_system,
                            hashed_password, is_active, is_verified, created_at, updated_at
                        ) VALUES (
                            :email, :username, :full_name, :age, :fitness_goal, :experience_level,
                            :account_type, :discoverability_level, :social_comfort_level,
                            :preferred_communication_style, :location_sharing_enabled,
                            :latitude, :longitude, :height, :weight, :unit_system,
                            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4tbQJ8Kz6G', true, true,
                            NOW(), NOW()
                        ) RETURNING id
                    """),
                    user_data
                )
                user_id = result.fetchone()[0]

            self.users.append({"id": user_id, **user_data})

        self.db.commit()
        print(f"✅ Created/Updated {len(self.users)} enhanced users")

    def create_communities(self):
        """Create diverse communities with different characteristics"""
        
        communities_data = [
            {
                "name": "Strength Warriors",
                "description": "Building strength together through structured workouts and progressive overload training. Perfect for those serious about getting stronger.",
                "category": "strength",
                "privacy_level": "public",
                "max_members": 1000,
                "is_official": True,
                "activity_level": "Very Active",
                "member_count": 2100,
                "challenge_active": True,
                "created_by": self.users[0]["id"]  # Sarah
            },
            {
                "name": "Early Birds",
                "description": "Morning workout enthusiasts who believe the early bird catches the gains! Rise and shine with our 5AM crew.",
                "category": "cardio",
                "privacy_level": "public",
                "max_members": 500,
                "is_official": False,
                "activity_level": "Active",
                "member_count": 1500,
                "challenge_active": False,
                "created_by": self.users[1]["id"]  # Mike
            },
            {
                "name": "Yoga Masters",
                "description": "Find your zen and flexibility through daily yoga practice and mindfulness. All levels welcome.",
                "category": "wellness",
                "privacy_level": "public",
                "max_members": 2000,
                "is_official": True,
                "activity_level": "Moderate",
                "member_count": 3200,
                "challenge_active": True,
                "created_by": self.users[2]["id"]  # Emma
            },
            {
                "name": "HIIT Squad",
                "description": "High-intensity interval training for maximum results in minimum time. Push your limits with our intense workouts.",
                "category": "hiit",
                "privacy_level": "public",
                "max_members": 800,
                "is_official": False,
                "activity_level": "Very Active",
                "member_count": 987,
                "challenge_active": True,
                "created_by": self.users[5]["id"]  # Alex
            },
            {
                "name": "Mindful Movers",
                "description": "Combining movement with mindfulness. Perfect for those who want to stay active while maintaining mental wellness.",
                "category": "wellness",
                "privacy_level": "public",
                "max_members": 1500,
                "is_official": False,
                "activity_level": "Moderate",
                "member_count": 1200,
                "challenge_active": False,
                "created_by": self.users[6]["id"]  # Nina
            },
            {
                "name": "Bodyweight Bros",
                "description": "No equipment needed! Master bodyweight exercises and calisthenics for functional strength.",
                "category": "strength",
                "privacy_level": "public",
                "max_members": 600,
                "is_official": False,
                "activity_level": "Active",
                "member_count": 743,
                "challenge_active": True,
                "created_by": self.users[7]["id"]  # James
            }
        ]

        for community_data in communities_data:
            # Check if community exists
            existing = self.db.execute(
                text("SELECT id FROM community_groups WHERE name = :name"),
                {"name": community_data["name"]}
            ).fetchone()

            if existing:
                # Update existing community
                self.db.execute(
                    text("""
                        UPDATE community_groups SET 
                            description = :description,
                            category = :category,
                            privacy_level = :privacy_level,
                            max_members = :max_members,
                            is_official = :is_official,
                            activity_level = :activity_level,
                            member_count = :member_count,
                            challenge_active = :challenge_active,
                            created_by = :created_by
                        WHERE name = :name
                    """),
                    community_data
                )
                community_id = existing[0]
            else:
                # Create new community
                result = self.db.execute(
                    text("""
                        INSERT INTO community_groups (
                            name, description, category, privacy_level, max_members,
                            is_official, activity_level, member_count, challenge_active,
                            created_by, created_at, updated_at
                        ) VALUES (
                            :name, :description, :category, :privacy_level, :max_members,
                            :is_official, :activity_level, :member_count, :challenge_active,
                            :created_by, NOW(), NOW()
                        ) RETURNING id
                    """),
                    community_data
                )
                community_id = result.fetchone()[0]

            self.communities.append({"id": community_id, **community_data})

        self.db.commit()
        print(f"✅ Created/Updated {len(self.communities)} communities")

    def create_community_memberships(self):
        """Create realistic community memberships"""
        
        # Define membership patterns
        membership_patterns = [
            # Sarah - Strength focused
            (0, 0, "admin"),  # Sarah in Strength Warriors as admin
            (0, 2, "member"),  # Sarah in Yoga Masters
            (0, 5, "member"),  # Sarah in Bodyweight Bros
            
            # Mike - Cardio focused
            (1, 1, "admin"),  # Mike in Early Birds as admin
            (1, 3, "member"),  # Mike in HIIT Squad
            (1, 0, "member"),  # Mike in Strength Warriors
            
            # Emma - Wellness focused
            (2, 2, "admin"),  # Emma in Yoga Masters as admin
            (2, 4, "member"),  # Emma in Mindful Movers
            
            # David - Strength focused
            (3, 0, "member"),  # David in Strength Warriors
            (3, 5, "member"),  # David in Bodyweight Bros
            (3, 3, "member"),  # David in HIIT Squad
            
            # Lisa - Strength focused
            (4, 0, "member"),  # Lisa in Strength Warriors
            (4, 5, "member"),  # Lisa in Bodyweight Bros
            
            # Alex - HIIT focused
            (5, 3, "admin"),  # Alex in HIIT Squad as admin
            (5, 1, "member"),  # Alex in Early Birds
            
            # Nina - Wellness focused
            (6, 4, "admin"),  # Nina in Mindful Movers as admin
            (6, 2, "member"),  # Nina in Yoga Masters
            
            # James - Strength focused
            (7, 5, "admin"),  # James in Bodyweight Bros as admin
            (7, 0, "member"),  # James in Strength Warriors
        ]

        for user_idx, community_idx, role in membership_patterns:
            user_id = self.users[user_idx]["id"]
            community_id = self.communities[community_idx]["id"]
            
            # Check if membership exists
            existing = self.db.execute(
                text("""
                    SELECT id FROM community_memberships 
                    WHERE user_id = :user_id AND group_id = :community_id
                """),
                {"user_id": user_id, "community_id": community_id}
            ).fetchone()

            if not existing:
                # Create membership
                self.db.execute(
                    text("""
                        INSERT INTO community_memberships (
                            user_id, group_id, joined_at, is_admin
                        ) VALUES (
                            :user_id, :group_id, NOW(), :is_admin
                        )
                    """),
                    {
                        "user_id": user_id,
                        "group_id": community_id,
                        "is_admin": role == "admin"
                    }
                )

                # Create community role
                self.db.execute(
                    text("""
                        INSERT INTO community_roles (
                            community_id, user_id, role_type, permissions, assigned_at
                        ) VALUES (
                            :community_id, :user_id, :role_type, :permissions, NOW()
                        )
                    """),
                    {
                        "community_id": community_id,
                        "user_id": user_id,
                        "role_type": role,
                        "permissions": {"can_moderate": role in ["admin", "moderator"], "can_invite": True}
                    }
                )

        self.db.commit()
        print(f"✅ Created community memberships and roles")

    def create_enhanced_challenges(self):
        """Create diverse challenges with different difficulty levels and success rates"""
        
        challenges_data = [
            {
                "name": "7-Day Movement Starter",
                "description": "Complete any 15-minute activity for 7 consecutive days. Perfect for building consistency and forming healthy habits.",
                "difficulty_level": "Accessible",
                "success_rate": 78.5,
                "challenge_type": "consistency",
                "participant_limit": 1000,
                "current_participants": 2100,
                "community_id": self.communities[4]["id"],  # Mindful Movers
                "target_audience": {
                    "experience_levels": ["beginner", "intermediate"],
                    "goals": ["wellness", "endurance"],
                    "time_commitment": "low"
                }
            },
            {
                "name": "Strength Foundation",
                "description": "3 strength workouts + 2 active recovery days. Build your base strength progressively with proper form.",
                "difficulty_level": "Stretch",
                "success_rate": 65.2,
                "challenge_type": "progression",
                "participant_limit": 500,
                "current_participants": 1500,
                "community_id": self.communities[0]["id"],  # Strength Warriors
                "target_audience": {
                    "experience_levels": ["intermediate", "advanced"],
                    "goals": ["strength"],
                    "time_commitment": "medium"
                }
            },
            {
                "name": "Complete Transformation",
                "description": "Daily workouts + nutrition tracking + mindfulness. Comprehensive lifestyle change for serious transformation.",
                "difficulty_level": "Ambitious",
                "success_rate": 42.8,
                "challenge_type": "lifestyle",
                "participant_limit": 200,
                "current_participants": 892,
                "community_id": self.communities[3]["id"],  # HIIT Squad
                "target_audience": {
                    "experience_levels": ["advanced"],
                    "goals": ["strength", "endurance", "wellness"],
                    "time_commitment": "high"
                }
            },
            {
                "name": "30-Day Yoga Journey",
                "description": "Daily yoga practice for 30 days. Improve flexibility, reduce stress, and find your inner peace.",
                "difficulty_level": "Accessible",
                "success_rate": 72.1,
                "challenge_type": "consistency",
                "participant_limit": 800,
                "current_participants": 2400,
                "community_id": self.communities[2]["id"],  # Yoga Masters
                "target_audience": {
                    "experience_levels": ["beginner", "intermediate"],
                    "goals": ["wellness"],
                    "time_commitment": "low"
                }
            },
            {
                "name": "Bodyweight Mastery",
                "description": "Master 10 essential bodyweight exercises. No equipment needed, just determination and consistency.",
                "difficulty_level": "Stretch",
                "success_rate": 58.9,
                "challenge_type": "skill",
                "participant_limit": 400,
                "current_participants": 743,
                "community_id": self.communities[5]["id"],  # Bodyweight Bros
                "target_audience": {
                    "experience_levels": ["intermediate"],
                    "goals": ["strength"],
                    "time_commitment": "medium"
                }
            }
        ]

        for challenge_data in challenges_data:
            # Check if challenge exists
            existing = self.db.execute(
                text("SELECT id FROM challenges WHERE name = :name"),
                {"name": challenge_data["name"]}
            ).fetchone()

            if existing:
                # Update existing challenge
                self.db.execute(
                    text("""
                        UPDATE challenges SET 
                            description = :description,
                            difficulty_level = :difficulty_level,
                            success_rate = :success_rate,
                            challenge_type = :challenge_type,
                            participant_limit = :participant_limit,
                            current_participants = :current_participants,
                            community_id = :community_id,
                            target_audience = :target_audience
                        WHERE name = :name
                    """),
                    challenge_data
                )
                challenge_id = existing[0]
            else:
                # Create new challenge
                result = self.db.execute(
                    text("""
                        INSERT INTO challenges (
                            name, description, difficulty_level, success_rate,
                            challenge_type, participant_limit, current_participants,
                            community_id, target_audience, start_date, end_date,
                            created_at, updated_at
                        ) VALUES (
                            :name, :description, :difficulty_level, :success_rate,
                            :challenge_type, :participant_limit, :current_participants,
                            :community_id, :target_audience, NOW(), 
                            NOW() + INTERVAL '30 days', NOW(), NOW()
                        ) RETURNING id
                    """),
                    challenge_data
                )
                challenge_id = result.fetchone()[0]

            self.challenges.append({"id": challenge_id, **challenge_data})

        self.db.commit()
        print(f"✅ Created/Updated {len(self.challenges)} enhanced challenges")

    def create_challenge_participants(self):
        """Create realistic challenge participation"""
        
        # Define participation patterns
        participation_patterns = [
            # Sarah - Active in strength challenges
            (0, 1, "active", 85.5),  # Sarah in Strength Foundation
            (0, 4, "active", 92.0),  # Sarah in Bodyweight Mastery
            
            # Mike - Active in cardio challenges
            (1, 0, "active", 78.0),  # Mike in Movement Starter
            (1, 2, "active", 45.0),  # Mike in Complete Transformation
            
            # Emma - Active in wellness challenges
            (2, 0, "active", 95.0),  # Emma in Movement Starter
            (2, 3, "active", 88.5),  # Emma in Yoga Journey
            
            # David - Active in strength challenges
            (3, 1, "active", 75.0),  # David in Strength Foundation
            (3, 4, "active", 80.0),  # David in Bodyweight Mastery
            
            # Lisa - Active in strength challenges
            (4, 1, "active", 82.0),  # Lisa in Strength Foundation
            (4, 4, "active", 90.0),  # Lisa in Bodyweight Mastery
            
            # Alex - Active in HIIT challenges
            (5, 2, "active", 60.0),  # Alex in Complete Transformation
            (5, 0, "completed", 100.0),  # Alex completed Movement Starter
            
            # Nina - Active in wellness challenges
            (6, 0, "active", 100.0),  # Nina in Movement Starter
            (6, 3, "active", 95.0),  # Nina in Yoga Journey
            
            # James - Active in strength challenges
            (7, 1, "active", 70.0),  # James in Strength Foundation
            (7, 4, "active", 85.0),  # James in Bodyweight Mastery
        ]

        for user_idx, challenge_idx, status, progress in participation_patterns:
            user_id = self.users[user_idx]["id"]
            challenge_id = self.challenges[challenge_idx]["id"]
            
            # Check if participation exists
            existing = self.db.execute(
                text("""
                    SELECT id FROM challenge_participants 
                    WHERE user_id = :user_id AND challenge_id = :challenge_id
                """),
                {"user_id": user_id, "challenge_id": challenge_id}
            ).fetchone()

            if not existing:
                # Create participation
                started_at = datetime.now() - timedelta(days=random.randint(1, 15))
                completed_at = None
                if status == "completed":
                    completed_at = started_at + timedelta(days=random.randint(7, 30))

                self.db.execute(
                    text("""
                        INSERT INTO challenge_participants (
                            challenge_id, user_id, status, progress_percentage,
                            started_at, completed_at
                        ) VALUES (
                            :challenge_id, :user_id, :status, :progress,
                            :started_at, :completed_at
                        )
                    """),
                    {
                        "challenge_id": challenge_id,
                        "user_id": user_id,
                        "status": status,
                        "progress": progress,
                        "started_at": started_at,
                        "completed_at": completed_at
                    }
                )

        self.db.commit()
        print(f"✅ Created challenge participants")

    def create_friend_invitations(self):
        """Create realistic friend invitations with different statuses"""
        
        invitation_data = [
            # Sarah's invitations
            {
                "inviter_id": self.users[0]["id"],  # Sarah
                "invitee_email": "friend1@example.com",
                "invitation_type": "email",
                "personalized_message": "Hey! I've been using this amazing fitness app and thought you'd love it too. We could be workout buddies!",
                "status": "pending",
                "created_at": datetime.now() - timedelta(days=2)
            },
            {
                "inviter_id": self.users[0]["id"],  # Sarah
                "invitee_email": "friend2@example.com",
                "invitation_type": "sms",
                "personalized_message": "Join me on FitTribe! Let's crush our fitness goals together 💪",
                "status": "accepted",
                "accepted_user_id": self.users[1]["id"],  # Mike
                "created_at": datetime.now() - timedelta(days=5),
                "accepted_at": datetime.now() - timedelta(days=3)
            },
            # Mike's invitations
            {
                "inviter_id": self.users[1]["id"],  # Mike
                "invitee_email": "friend3@example.com",
                "invitation_type": "email",
                "personalized_message": "Looking for a running buddy! This app has been great for finding motivated people.",
                "status": "expired",
                "created_at": datetime.now() - timedelta(days=30)
            },
            # Emma's invitations
            {
                "inviter_id": self.users[2]["id"],  # Emma
                "invitee_email": "friend4@example.com",
                "invitation_type": "qr_code",
                "personalized_message": "Let's start our wellness journey together! This app has amazing yoga communities.",
                "status": "pending",
                "created_at": datetime.now() - timedelta(days=1)
            }
        ]

        for invitation in invitation_data:
            # Generate unique invitation code
            invitation_code = str(uuid.uuid4())
            
            # Set expiration date
            expires_at = invitation["created_at"] + timedelta(days=7)
            
            self.db.execute(
                text("""
                    INSERT INTO friend_invitations (
                        inviter_id, invitee_email, invitation_type, invitation_code,
                        personalized_message, status, accepted_user_id, created_at,
                        expires_at, accepted_at
                    ) VALUES (
                        :inviter_id, :invitee_email, :invitation_type, :invitation_code,
                        :personalized_message, :status, :accepted_user_id, :created_at,
                        :expires_at, :accepted_at
                    )
                """),
                {
                    **invitation,
                    "invitation_code": invitation_code,
                    "expires_at": expires_at
                }
            )

        self.db.commit()
        print(f"✅ Created friend invitations")

    def create_accountability_partnerships(self):
        """Create realistic accountability partnerships"""
        
        partnership_data = [
            # Sarah and Mike - workout partners
            {
                "user_id": self.users[0]["id"],  # Sarah
                "partner_id": self.users[1]["id"],  # Mike
                "partnership_type": "workout_partner",
                "goal_compatibility_score": 0.85,
                "schedule_compatibility_score": 0.90,
                "personality_compatibility_score": 0.88
            },
            # Emma and Nina - goal supporters
            {
                "user_id": self.users[2]["id"],  # Emma
                "partner_id": self.users[6]["id"],  # Nina
                "partnership_type": "goal_supporter",
                "goal_compatibility_score": 0.95,
                "schedule_compatibility_score": 0.75,
                "personality_compatibility_score": 0.92
            },
            # David and James - progress checkers
            {
                "user_id": self.users[3]["id"],  # David
                "partner_id": self.users[7]["id"],  # James
                "partnership_type": "progress_checker",
                "goal_compatibility_score": 0.88,
                "schedule_compatibility_score": 0.70,
                "personality_compatibility_score": 0.85
            },
            # Lisa and Alex - workout partners
            {
                "user_id": self.users[4]["id"],  # Lisa
                "partner_id": self.users[5]["id"],  # Alex
                "partnership_type": "workout_partner",
                "goal_compatibility_score": 0.78,
                "schedule_compatibility_score": 0.85,
                "personality_compatibility_score": 0.80
            }
        ]

        for partnership in partnership_data:
            # Check if partnership exists
            existing = self.db.execute(
                text("""
                    SELECT id FROM accountability_partnerships 
                    WHERE (user_id = :user_id AND partner_id = :partner_id)
                       OR (user_id = :partner_id AND partner_id = :user_id)
                """),
                {"user_id": partnership["user_id"], "partner_id": partnership["partner_id"]}
            ).fetchone()

            if not existing:
                self.db.execute(
                    text("""
                        INSERT INTO accountability_partnerships (
                            user_id, partner_id, partnership_type, status,
                            goal_compatibility_score, schedule_compatibility_score,
                            personality_compatibility_score, created_at
                        ) VALUES (
                            :user_id, :partner_id, :partnership_type, 'active',
                            :goal_compatibility_score, :schedule_compatibility_score,
                            :personality_compatibility_score, NOW()
                        )
                    """),
                    partnership
                )

        self.db.commit()
        print(f"✅ Created accountability partnerships")

    def create_privacy_controls(self):
        """Create privacy controls for different user types"""
        
        privacy_controls = [
            # Sarah - Public user, shares most things
            {
                "user_id": self.users[0]["id"],
                "control_type": "profile_visibility",
                "target_group": "public",
                "is_enabled": True
            },
            {
                "user_id": self.users[0]["id"],
                "control_type": "workout_sharing",
                "target_group": "friends",
                "is_enabled": True
            },
            {
                "user_id": self.users[0]["id"],
                "control_type": "location_sharing",
                "target_group": "friends",
                "is_enabled": True
            },
            
            # Emma - Private user, very selective
            {
                "user_id": self.users[2]["id"],
                "control_type": "profile_visibility",
                "target_group": "friends",
                "is_enabled": True
            },
            {
                "user_id": self.users[2]["id"],
                "control_type": "workout_sharing",
                "target_group": "specific_users",
                "is_enabled": True,
                "specific_user_ids": [self.users[6]["id"]]  # Only Nina
            },
            {
                "user_id": self.users[2]["id"],
                "control_type": "location_sharing",
                "target_group": "friends",
                "is_enabled": False
            },
            
            # Lisa - Semi-private user
            {
                "user_id": self.users[4]["id"],
                "control_type": "profile_visibility",
                "target_group": "community",
                "is_enabled": True
            },
            {
                "user_id": self.users[4]["id"],
                "control_type": "workout_sharing",
                "target_group": "friends",
                "is_enabled": True
            },
            {
                "user_id": self.users[4]["id"],
                "control_type": "location_sharing",
                "target_group": "community",
                "is_enabled": True
            }
        ]

        for control in privacy_controls:
            # Check if control exists
            existing = self.db.execute(
                text("""
                    SELECT id FROM privacy_controls 
                    WHERE user_id = :user_id AND control_type = :control_type
                """),
                {"user_id": control["user_id"], "control_type": control["control_type"]}
            ).fetchone()

            if not existing:
                self.db.execute(
                    text("""
                        INSERT INTO privacy_controls (
                            user_id, control_type, target_group, is_enabled,
                            specific_user_ids, created_at
                        ) VALUES (
                            :user_id, :control_type, :target_group, :is_enabled,
                            :specific_user_ids, NOW()
                        )
                    """),
                    control
                )

        self.db.commit()
        print(f"✅ Created privacy controls")

    def create_user_subscriptions(self):
        """Create premium subscriptions for some users"""
        
        subscription_data = [
            {
                "user_id": self.users[0]["id"],  # Sarah
                "subscription_type": "premium",
                "features": {
                    "priority_matching": True,
                    "advanced_analytics": True,
                    "custom_challenges": True,
                    "video_calls": True
                },
                "expires_at": datetime.now() + timedelta(days=365)
            },
            {
                "user_id": self.users[3]["id"],  # David
                "subscription_type": "premium_safety",
                "features": {
                    "priority_matching": True,
                    "advanced_analytics": True,
                    "custom_challenges": True,
                    "video_calls": True,
                    "enhanced_verification": True,
                    "advanced_reporting": True,
                    "direct_support": True
                },
                "expires_at": datetime.now() + timedelta(days=180)
            },
            {
                "user_id": self.users[6]["id"],  # Nina
                "subscription_type": "premium",
                "features": {
                    "priority_matching": True,
                    "advanced_analytics": True,
                    "custom_challenges": True,
                    "video_calls": True
                },
                "expires_at": datetime.now() + timedelta(days=90)
            }
        ]

        for subscription in subscription_data:
            # Check if subscription exists
            existing = self.db.execute(
                text("SELECT id FROM user_subscriptions WHERE user_id = :user_id"),
                {"user_id": subscription["user_id"]}
            ).fetchone()

            if not existing:
                self.db.execute(
                    text("""
                        INSERT INTO user_subscriptions (
                            user_id, subscription_type, status, features,
                            started_at, expires_at
                        ) VALUES (
                            :user_id, :subscription_type, 'active', :features,
                            NOW(), :expires_at
                        )
                    """),
                    subscription
                )

        self.db.commit()
        print(f"✅ Created user subscriptions")

    def create_content_reports(self):
        """Create some content reports for testing moderation"""
        
        report_data = [
            {
                "reporter_id": self.users[2]["id"],  # Emma
                "reported_content_type": "post",
                "reported_content_id": 1,
                "report_reason": "inappropriate_content",
                "report_details": "This post contains inappropriate language and doesn't align with our community guidelines.",
                "ai_analysis_score": 0.85
            },
            {
                "reporter_id": self.users[6]["id"],  # Nina
                "reported_content_type": "message",
                "reported_content_id": 2,
                "report_reason": "harassment",
                "report_details": "Received unwanted messages that made me feel uncomfortable.",
                "ai_analysis_score": 0.92
            },
            {
                "reporter_id": self.users[0]["id"],  # Sarah
                "reported_content_type": "profile",
                "reported_content_id": 3,
                "report_reason": "spam",
                "report_details": "This profile appears to be promoting external services.",
                "ai_analysis_score": 0.78
            }
        ]

        for report in report_data:
            self.db.execute(
                text("""
                    INSERT INTO content_reports (
                        reporter_id, reported_content_type, reported_content_id,
                        report_reason, report_details, status, ai_analysis_score,
                        created_at
                    ) VALUES (
                        :reporter_id, :reported_content_type, :reported_content_id,
                        :report_reason, :report_details, 'pending', :ai_analysis_score,
                        NOW()
                    )
                """),
                report
            )

        self.db.commit()
        print(f"✅ Created content reports")

    def run(self):
        """Run the complete mock data population"""
        print("🚀 Starting enhanced mock data population...")
        
        try:
            self.create_enhanced_users()
            self.create_communities()
            self.create_community_memberships()
            self.create_enhanced_challenges()
            self.create_challenge_participants()
            self.create_friend_invitations()
            self.create_accountability_partnerships()
            self.create_privacy_controls()
            self.create_user_subscriptions()
            self.create_content_reports()
            
            print("✅ Enhanced mock data population completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during mock data population: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()


if __name__ == "__main__":
    populator = EnhancedMockDataPopulator()
    populator.run() 