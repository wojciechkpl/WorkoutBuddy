"""
Authentication Service Implementation
Demonstrates dependency injection usage with the new container system
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from app.core.service_registration import (
    IAuthService,
    IUserRepository,
    ICacheManager,
    IEmailService,
)
from app.core.config import SecurityConfig

logger = logging.getLogger(__name__)


class AuthService(IAuthService):
    """Authentication service implementation"""

    def __init__(
        self,
        user_repository: IUserRepository,
        cache_manager: ICacheManager,
        email_service: IEmailService,
        security_config: SecurityConfig,
    ):
        self.user_repository = user_repository
        self.cache_manager = cache_manager
        self.email_service = email_service
        self.security_config = security_config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        logger.info("AuthService initialized with dependency injection")

    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        """Authenticate user with username/email and password"""
        try:
            # Try to find user by email first
            user = await self.user_repository.get_by_email(username)

            if not user:
                logger.warning(f"Authentication failed: user not found for {username}")
                return None

            # Verify password
            if not self._verify_password(password, user.hashed_password):
                logger.warning(
                    f"Authentication failed: invalid password for {username}"
                )
                return None

            # Update last login
            await self.user_repository.update(
                user.id, {"last_login": datetime.utcnow()}
            )

            logger.info(f"User {username} authenticated successfully")
            return user

        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return None

    async def create_token(self, user: Any) -> str:
        """Create JWT token for user"""
        try:
            # Create token payload
            payload = {
                "sub": str(user.id),
                "email": user.email,
                "exp": datetime.utcnow()
                + timedelta(minutes=self.security_config.access_token_expire_minutes),
                "iat": datetime.utcnow(),
                "type": "access",
            }

            # Create token
            token = jwt.encode(
                payload,
                self.security_config.secret_key,
                algorithm=self.security_config.algorithm,
            )

            # Cache token for blacklist checking
            await self.cache_manager.set(
                f"token:{token}",
                {"user_id": user.id, "exp": payload["exp"].timestamp()},
                ttl=self.security_config.access_token_expire_minutes * 60,
            )

            logger.info(f"Token created for user {user.id}")
            return token

        except Exception as e:
            logger.error(f"Token creation error for user {user.id}: {e}")
            raise

    async def validate_token(self, token: str) -> Optional[Any]:
        """Validate JWT token and return user"""
        try:
            # Check if token is blacklisted
            cached_token = await self.cache_manager.get(f"token:{token}")
            if not cached_token:
                logger.warning("Token validation failed: token not found in cache")
                return None

            # Decode token
            payload = jwt.decode(
                token,
                self.security_config.secret_key,
                algorithms=[self.security_config.algorithm],
            )

            # Get user
            user = await self.user_repository.get_by_id(int(payload["sub"]))
            if not user:
                logger.warning(
                    f"Token validation failed: user {payload['sub']} not found"
                )
                return None

            logger.info(f"Token validated for user {user.id}")
            return user

        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: invalid token - {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    async def create_refresh_token(self, user: Any) -> str:
        """Create refresh token for user"""
        try:
            payload = {
                "sub": str(user.id),
                "exp": datetime.utcnow()
                + timedelta(days=self.security_config.refresh_token_expire_days),
                "iat": datetime.utcnow(),
                "type": "refresh",
            }

            token = jwt.encode(
                payload,
                self.security_config.secret_key,
                algorithm=self.security_config.algorithm,
            )

            # Cache refresh token
            await self.cache_manager.set(
                f"refresh_token:{token}",
                {"user_id": user.id, "exp": payload["exp"].timestamp()},
                ttl=self.security_config.refresh_token_expire_days * 24 * 60 * 60,
            )

            logger.info(f"Refresh token created for user {user.id}")
            return token

        except Exception as e:
            logger.error(f"Refresh token creation error for user {user.id}: {e}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            # Validate refresh token
            payload = jwt.decode(
                refresh_token,
                self.security_config.secret_key,
                algorithms=[self.security_config.algorithm],
            )

            if payload.get("type") != "refresh":
                logger.warning("Token refresh failed: not a refresh token")
                return None

            # Check if refresh token is cached
            cached_token = await self.cache_manager.get(
                f"refresh_token:{refresh_token}"
            )
            if not cached_token:
                logger.warning("Token refresh failed: refresh token not found in cache")
                return None

            # Get user
            user = await self.user_repository.get_by_id(int(payload["sub"]))
            if not user:
                logger.warning(f"Token refresh failed: user {payload['sub']} not found")
                return None

            # Create new access token
            new_token = await self.create_token(user)

            logger.info(f"Access token refreshed for user {user.id}")
            return new_token

        except jwt.ExpiredSignatureError:
            logger.warning("Token refresh failed: refresh token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token refresh failed: invalid refresh token - {e}")
            return None
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

    async def revoke_token(self, token: str) -> bool:
        """Revoke/blacklist a token"""
        try:
            # Remove from cache (blacklist)
            await self.cache_manager.delete(f"token:{token}")
            await self.cache_manager.delete(f"refresh_token:{token}")

            logger.info("Token revoked successfully")
            return True

        except Exception as e:
            logger.error(f"Token revocation error: {e}")
            return False

    async def register_user(self, user_data: Dict[str, Any]) -> Optional[Any]:
        """Register a new user"""
        try:
            # Validate password
            if not self._validate_password(user_data["password"]):
                raise ValueError("Password does not meet requirements")

            # Hash password
            hashed_password = self._hash_password(user_data["password"])

            # Create user data
            user_create_data = {
                "email": user_data["email"],
                "username": user_data.get("username"),
                "hashed_password": hashed_password,
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "created_at": datetime.utcnow(),
                "is_active": True,
            }

            # Create user
            user = await self.user_repository.create(user_create_data)

            # Send welcome email
            if self.email_service:
                await self.email_service.send_welcome_email(user)

            logger.info(f"User registered successfully: {user.email}")
            return user

        except Exception as e:
            logger.error(f"User registration error: {e}")
            raise

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(password, hashed_password)

    def _validate_password(self, password: str) -> bool:
        """Validate password meets requirements"""
        if len(password) < self.security_config.password_min_length:
            return False

        if self.security_config.password_require_special and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            return False

        if self.security_config.password_require_numbers and not any(
            c.isdigit() for c in password
        ):
            return False

        if self.security_config.password_require_uppercase and not any(
            c.isupper() for c in password
        ):
            return False

        return True

    async def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        try:
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return False

            # Verify old password
            if not self._verify_password(old_password, user.hashed_password):
                return False

            # Validate new password
            if not self._validate_password(new_password):
                return False

            # Hash new password
            new_hashed_password = self._hash_password(new_password)

            # Update user
            await self.user_repository.update(
                user_id,
                {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow(),
                },
            )

            logger.info(f"Password changed for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Password change error for user {user_id}: {e}")
            return False

    async def reset_password_request(self, email: str) -> bool:
        """Request password reset"""
        try:
            # Get user
            user = await self.user_repository.get_by_email(email)
            if not user:
                # Don't reveal if user exists
                logger.info(f"Password reset requested for email: {email}")
                return True

            # Generate reset token
            reset_token = self._generate_reset_token()

            # Cache reset token
            await self.cache_manager.set(
                f"reset_token:{reset_token}",
                {"user_id": user.id, "email": email},
                ttl=3600,  # 1 hour
            )

            # Send reset email
            if self.email_service:
                await self.email_service.send_email(
                    email,
                    "Password Reset Request",
                    f"Your password reset token is: {reset_token}",
                )

            logger.info(f"Password reset requested for user {user.id}")
            return True

        except Exception as e:
            logger.error(f"Password reset request error: {e}")
            return False

    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            # Get reset token from cache
            reset_data = await self.cache_manager.get(f"reset_token:{reset_token}")
            if not reset_data:
                return False

            # Validate new password
            if not self._validate_password(new_password):
                return False

            # Hash new password
            new_hashed_password = self._hash_password(new_password)

            # Update user
            await self.user_repository.update(
                reset_data["user_id"],
                {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow(),
                },
            )

            # Remove reset token
            await self.cache_manager.delete(f"reset_token:{reset_token}")

            logger.info(f"Password reset for user {reset_data['user_id']}")
            return True

        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return False

    def _generate_reset_token(self) -> str:
        """Generate a random reset token"""
        import secrets

        return secrets.token_urlsafe(32)
