"""
Enhanced Social Features Tests

Tests for the new social features described in the customer journey document:
- Friend invitation system
- Community management
- Privacy controls
- Account types
- Safety and moderation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.main import app
from app.models.user import User
from app.models.friendship import Friendship
from app.models.community import CommunityGroup, CommunityMembership
from app.models.challenge import Challenge
from app.models.privacy import PrivacySetting
from app.models.safety import UserBlock, UserReport
from app.database import get_db
from tests.conftest import create_test_user, get_test_token


class TestFriendInvitationSystem:
    """Test the enhanced friend invitation system"""

    def test_send_friend_invitation_email(self, client: TestClient, db_session: Session):
        """Test sending friend invitation via email"""
        # Create test users
        user1 = create_test_user(db_session, "inviter@test.com", "inviter")
        user2 = create_test_user(db_session, "invitee@test.com", "invitee")
        
        token = get_test_token(user1)
        print(f"Generated token: {token}")
        
        response = client.post(
            "/api/v1/social/invitations/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "invitee_email": "friend@example.com",
                "invitation_type": "email",
                "personalized_message": "Join me on FitTribe! Let's crush our fitness goals together 💪"
            }
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert "invitation_code" in data
        assert data["status"] == "pending"
        assert data["invitation_type"] == "email"

    def test_send_friend_invitation_sms(self, client: TestClient, db_session: Session):
        """Test sending friend invitation via SMS"""
        user = create_test_user(db_session, "inviter@test.com", "inviter")
        token = get_test_token(user)
        
        response = client.post(
            "/api/v1/social/invitations/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "invitee_phone": "+1234567890",
                "invitation_type": "sms",
                "personalized_message": "Hey! Join me on FitTribe for amazing workouts!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["invitation_type"] == "sms"

    def test_accept_friend_invitation(self, client: TestClient, db_session: Session):
        """Test accepting a friend invitation"""
        # Create invitation in database
        user1 = create_test_user(db_session, "inviter@test.com", "inviter")
        user2 = create_test_user(db_session, "invitee@test.com", "invitee")
        
        # Create invitation
        invitation_code = "test_invitation_123"
        db_session.execute(
            text("INSERT INTO friend_invitations (inviter_id, invitee_email, invitation_code, invitation_type, status) VALUES (:inviter_id, :email, :code, 'email', 'pending')"),
            {"inviter_id": user1.id, "email": "invitee@test.com", "code": invitation_code}
        )
        db_session.commit()
        
        token = get_test_token(user2)
        
        response = client.post(
            f"/api/v1/social/invitations/accept/{invitation_code}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"

    def test_get_invitation_status(self, client: TestClient, db_session: Session):
        """Test getting invitation status dashboard"""
        user = create_test_user(db_session, "inviter@test.com", "inviter")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/social/invitations/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "invitations" in data
        assert "analytics" in data

    def test_import_contacts(self, client: TestClient, db_session: Session):
        """Test contact import functionality"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        contacts = [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "phone": "+1234567890"},
            {"name": "Bob Wilson", "email": "bob@example.com", "phone": "+0987654321"}
        ]
        
        response = client.post(
            "/api/v1/social/invitations/import-contacts",
            headers={"Authorization": f"Bearer {token}"},
            json={"contacts": contacts}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "existing_users" in data
        assert "new_invitations" in data


class TestCommunityManagement:
    """Test community management features"""

    def test_create_community(self, client: TestClient, db_session: Session):
        """Test creating a new community"""
        user = create_test_user(db_session, "creator@test.com", "creator")
        token = get_test_token(user)
        
        community_data = {
            "name": "Test Community",
            "description": "A test community for fitness enthusiasts",
            "category": "strength",
            "privacy_level": "public",
            "max_members": 100
        }
        
        response = client.post(
            "/api/v1/community/",
            headers={"Authorization": f"Bearer {token}"},
            json=community_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Community"
        assert data["created_by"] == user.id

    def test_join_community(self, client: TestClient, db_session: Session):
        """Test joining a community"""
        user = create_test_user(db_session, "user@test.com", "user")
        community = db_session.query(CommunityGroup).first()
        
        if not community:
            # Create a test community
            community = CommunityGroup(
                name="Test Community",
                description="Test description",
                category="strength",
                privacy_level="public"
            )
            db_session.add(community)
            db_session.commit()
        
        token = get_test_token(user)
        
        response = client.post(
            f"/api/v1/community/{community.id}/join",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "joined"

    def test_get_community_recommendations(self, client: TestClient, db_session: Session):
        """Test getting personalized community recommendations"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/community/recommendations",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data

    def test_community_matching_algorithm(self, client: TestClient, db_session: Session):
        """Test the community matching algorithm"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/community/matching",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data


class TestPrivacyControls:
    """Test privacy control features"""

    def test_set_privacy_controls(self, client: TestClient, db_session: Session):
        """Test setting privacy controls"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        privacy_settings = {
            "profile_visibility": {
                "target_group": "friends",
                "is_enabled": True
            },
            "workout_sharing": {
                "target_group": "community",
                "is_enabled": True
            },
            "location_sharing": {
                "target_group": "friends",
                "is_enabled": False
            }
        }
        
        response = client.post(
            "/api/v1/privacy/controls",
            headers={"Authorization": f"Bearer {token}"},
            json=privacy_settings
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_get_privacy_controls(self, client: TestClient, db_session: Session):
        """Test getting privacy controls"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/privacy/controls",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "profile_visibility" in data

    def test_account_type_management(self, client: TestClient, db_session: Session):
        """Test account type management"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        # Test changing account type
        response = client.post(
            "/api/v1/privacy/account-type",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "account_type": "private",
                "discoverability_level": "friends_only"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestSafetyAndModeration:
    """Test safety and moderation features"""

    def test_block_user(self, client: TestClient, db_session: Session):
        """Test blocking a user"""
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        token = get_test_token(user1)
        
        response = client.post(
            "/api/v1/safety/block",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "blocked_user_id": user2.id,
                "block_reason": "inappropriate_behavior",
                "block_type": "user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_report_content(self, client: TestClient, db_session: Session):
        """Test reporting content"""
        user = create_test_user(db_session, "reporter@test.com", "reporter")
        token = get_test_token(user)
        
        report_data = {
            "reported_content_type": "post",
            "reported_content_id": 1,
            "report_reason": "inappropriate_content",
            "report_details": "This post contains inappropriate language"
        }
        
        response = client.post(
            "/api/v1/safety/report",
            headers={"Authorization": f"Bearer {token}"},
            json=report_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_get_safety_status(self, client: TestClient, db_session: Session):
        """Test getting safety status and statistics"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/safety/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "blocked_users" in data


class TestChallengeSystem:
    """Test enhanced challenge system"""

    def test_get_personalized_challenges(self, client: TestClient, db_session: Session):
        """Test getting personalized challenges"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/challenges/personalized",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "challenges" in data

    def test_join_challenge(self, client: TestClient, db_session: Session):
        """Test joining a challenge"""
        user = create_test_user(db_session, "user@test.com", "user")
        challenge = db_session.query(Challenge).first()
        
        if not challenge:
            # Create a test challenge
            from datetime import datetime, timedelta
            from app.schemas.challenge import ChallengeType, ChallengeStatus
            
            challenge = Challenge(
                title="Test Challenge",
                description="Test challenge description",
                challenge_type=ChallengeType.WORKOUT,
                target_value=100.0,
                target_unit="reps",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                created_by=user.id
            )
            db_session.add(challenge)
            db_session.commit()
        
        token = get_test_token(user)
        
        response = client.post(
            f"/api/v1/challenges/{challenge.id}/join",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_update_challenge_progress(self, client: TestClient, db_session: Session):
        """Test updating challenge progress"""
        user = create_test_user(db_session, "user@test.com", "user")
        challenge = db_session.query(Challenge).first()
        
        if not challenge:
            from datetime import datetime, timedelta
            from app.schemas.challenge import ChallengeType, ChallengeStatus
            
            challenge = Challenge(
                title="Test Challenge",
                description="Test challenge description",
                challenge_type=ChallengeType.WORKOUT,
                target_value=100.0,
                target_unit="reps",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                created_by=user.id
            )
            db_session.add(challenge)
            db_session.commit()
        
        token = get_test_token(user)
        
        response = client.put(
            f"/api/v1/challenges/{challenge.id}/progress",
            headers={"Authorization": f"Bearer {token}"},
            json={"progress_percentage": 75.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestAccountabilitySystem:
    """Test accountability partnership system"""

    def test_create_accountability_partnership(self, client: TestClient, db_session: Session):
        """Test creating an accountability partnership"""
        user1 = create_test_user(db_session, "user1@test.com", "user1")
        user2 = create_test_user(db_session, "user2@test.com", "user2")
        token = get_test_token(user1)
        
        partnership_data = {
            "partner_id": user2.id,
            "partnership_type": "workout_partner",
            "goal_compatibility_score": 0.85,
            "schedule_compatibility_score": 0.90,
            "personality_compatibility_score": 0.88
        }
        
        response = client.post(
            "/api/v1/accountability/partnerships",
            headers={"Authorization": f"Bearer {token}"},
            json=partnership_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_get_accountability_partners(self, client: TestClient, db_session: Session):
        """Test getting accountability partners"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/accountability/partners",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "partners" in data

    def test_create_accountability_checkin(self, client: TestClient, db_session: Session):
        """Test creating an accountability check-in"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        checkin_data = {
            "checkin_type": "workout",
            "status": "completed",
            "notes": "Great workout today!",
            "shared_with_partner": True
        }
        
        response = client.post(
            "/api/v1/accountability/checkins",
            headers={"Authorization": f"Bearer {token}"},
            json=checkin_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestPremiumFeatures:
    """Test premium subscription features"""

    def test_get_premium_features(self, client: TestClient, db_session: Session):
        """Test getting premium features for a user"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        response = client.get(
            "/api/v1/subscriptions/features",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "features" in data

    def test_upgrade_to_premium(self, client: TestClient, db_session: Session):
        """Test upgrading to premium subscription"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        upgrade_data = {
            "subscription_type": "premium",
            "payment_method": "test_payment"
        }
        
        response = client.post(
            "/api/v1/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {token}"},
            json=upgrade_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestIntegrationScenarios:
    """Test integration scenarios from customer journey"""

    def test_complete_onboarding_flow(self, client: TestClient, db_session: Session):
        """Test complete onboarding flow with privacy and safety setup"""
        # Step 1: Create user
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        # Step 2: Login to get access token
        login_data = {"username": user_data["username"], "password": user_data["password"]}
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Step 3: Complete fitness assessment
        assessment_data = {
            "fitness_level": "beginner",
            "primary_goals": ["strength"],
            "time_commitment": "30min",
            "preferred_workout_types": ["strength_training"],
            "preferred_times": ["morning"]
        }
        
        response = client.post(
            "/api/v1/users/fitness-assessment",
            headers={"Authorization": f"Bearer {token}"},
            json=assessment_data
        )
        assert response.status_code == 200
        
        # Step 4: Set privacy preferences
        privacy_data = {
            "account_type": "public",
            "discoverability_level": "all",
            "social_comfort_level": "medium",
            "location_sharing_enabled": True
        }
        
        response = client.post(
            "/api/v1/users/privacy-setup",
            headers={"Authorization": f"Bearer {token}"},
            json=privacy_data
        )
        assert response.status_code == 200
        
        # Step 5: Set goals
        goal_data = {
            "primary_goal": "strength",
            "timeline": "3_months",
            "milestones": ["Complete first workout", "Join a community"]
        }
        
        response = client.post(
            "/api/v1/users/goals",
            headers={"Authorization": f"Bearer {token}"},
            json=goal_data
        )
        assert response.status_code == 200
        
        # Step 6: Get personalized recommendations
        response = client.get(
            "/api/v1/recommendations/onboarding",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "challenges" in data
        assert "communities" in data
        assert "friends_suggestions" in data

    def test_friend_invitation_workflow(self, client: TestClient, db_session: Session):
        """Test complete friend invitation workflow"""
        # Create two users
        user1 = create_test_user(db_session, "inviter@test.com", "inviter")
        user2 = create_test_user(db_session, "invitee@test.com", "invitee")
        
        token1 = get_test_token(user1)
        token2 = get_test_token(user2)
        
        # Step 1: Send invitation
        invitation_data = {
            "invitee_email": "invitee@test.com",
            "invitation_type": "email",
            "personalized_message": "Join me on FitTribe!"
        }
        
        response = client.post(
            "/api/v1/social/invitations/send",
            headers={"Authorization": f"Bearer {token1}"},
            json=invitation_data
        )
        assert response.status_code == 200
        
        invitation_code = response.json()["invitation_code"]
        
        # Step 2: Accept invitation
        response = client.post(
            f"/api/v1/social/invitations/accept/{invitation_code}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 200
        
        # Step 3: Verify friendship created
        response = client.get(
            "/api/v1/social/friends",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 200
        friends = response.json()
        assert len(friends) == 1
        assert friends[0]["username"] == "invitee"

    def test_community_matching_and_joining(self, client: TestClient, db_session: Session):
        """Test community matching and joining workflow"""
        user = create_test_user(db_session, "user@test.com", "user")
        token = get_test_token(user)
        
        # Step 1: Get community recommendations
        response = client.get(
            "/api/v1/community/recommendations",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        communities = response.json()["communities"]
        if communities:
            community_id = communities[0]["id"]
            
            # Step 2: Join community
            response = client.post(
                f"/api/v1/community/{community_id}/join",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            
            # Step 3: Get community challenges
            response = client.get(
                f"/api/v1/community/{community_id}/challenges",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

    def test_safety_incident_response(self, client: TestClient, db_session: Session):
        """Test safety incident response workflow"""
        user1 = create_test_user(db_session, "reporter@test.com", "reporter")
        user2 = create_test_user(db_session, "reported@test.com", "reported")
        token = get_test_token(user1)
        
        # Step 1: Report user
        report_data = {
            "reported_user_id": user2.id,
            "report_reason": "harassment",
            "report_details": "Received unwanted messages"
        }
        
        response = client.post(
            "/api/v1/safety/report",
            headers={"Authorization": f"Bearer {token}"},
            json=report_data
        )
        assert response.status_code == 200
        
        # Step 2: Block user
        block_data = {
            "blocked_user_id": user2.id,
            "block_reason": "harassment",
            "block_type": "user"
        }
        
        response = client.post(
            "/api/v1/safety/block",
            headers={"Authorization": f"Bearer {token}"},
            json=block_data
        )
        assert response.status_code == 200
        
        # Step 3: Verify user is blocked
        response = client.get(
            "/api/v1/safety/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        blocked_users = response.json()["blocked_users"]
        assert len(blocked_users) == 1
        assert blocked_users[0]["user_id"] == user2.id 