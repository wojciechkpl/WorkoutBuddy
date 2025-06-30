#!/usr/bin/env python3
"""
Script to fix password hashing for test users
"""

from app.database import get_db
from app.api.auth import get_password_hash
from app.models.user import User


def fix_test_user_passwords():
    """Fix password hashing for test users"""
    db = next(get_db())

    try:
        # Get all test users
        test_users = (
            db.query(User)
            .filter(
                User.username.in_(
                    [
                        "testuser",
                        "test_fitness_newbie",
                        "test_workout_warrior",
                        "test_gym_buddy",
                        "test_fitness_pro",
                    ]
                )
            )
            .all()
        )

        for user in test_users:
            # Update password hash
            user.hashed_password = get_password_hash("testpassword123")
            print(f"Updated password for user: {user.username}")

        db.commit()
        print("All test user passwords updated successfully!")

    except Exception as e:
        print(f"Error updating passwords: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    fix_test_user_passwords()
