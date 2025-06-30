"""
Service Registration System for Pulse Fitness
Handles service registration patterns, factory patterns, and interface binding
"""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from abc import ABC, abstractmethod
import logging
from functools import wraps

from .container import ServiceContainer, ServiceLifetime
from .config import get_config, get_database_config, get_redis_config, get_ml_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Interface definitions
class IUserRepository(ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def update(self, user_id: int, user_data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass


class IChallengeRepository(ABC):
    """Challenge repository interface"""

    @abstractmethod
    async def get_by_id(self, challenge_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    async def get_user_challenges(self, user_id: int) -> List[Any]:
        pass

    @abstractmethod
    async def create(self, challenge_data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def update(self, challenge_id: int, challenge_data: Dict[str, Any]) -> Any:
        pass


class IAuthService(ABC):
    """Authentication service interface"""

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def create_token(self, user: Any) -> str:
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Any]:
        pass


class IChallengeService(ABC):
    """Challenge service interface"""

    @abstractmethod
    async def create_challenge(
        self, user_id: int, challenge_data: Dict[str, Any]
    ) -> Any:
        pass

    @abstractmethod
    async def get_user_challenges(self, user_id: int) -> List[Any]:
        pass

    @abstractmethod
    async def complete_challenge(self, user_id: int, challenge_id: int) -> bool:
        pass


class IRecommendationService(ABC):
    """ML recommendation service interface"""

    @abstractmethod
    async def get_exercise_recommendations(
        self, user_id: int, count: int = 10
    ) -> List[Any]:
        pass

    @abstractmethod
    async def get_challenge_recommendations(
        self, user_id: int, count: int = 5
    ) -> List[Any]:
        pass


class IEmbeddingService(ABC):
    """User embedding service interface"""

    @abstractmethod
    async def create_user_embedding(self, user_data: Dict[str, Any]) -> List[float]:
        pass

    @abstractmethod
    async def find_similar_users(self, user_id: int, count: int = 5) -> List[Any]:
        pass


class IEmailService(ABC):
    """Email service interface"""

    @abstractmethod
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        pass

    @abstractmethod
    async def send_welcome_email(self, user: Any) -> bool:
        pass


class IStorageService(ABC):
    """File storage service interface"""

    @abstractmethod
    async def upload_file(
        self, file_data: bytes, filename: str, content_type: str
    ) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        pass


class ICacheManager(ABC):
    """Cache manager interface"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def clear(self) -> bool:
        pass


class INotificationService(ABC):
    """Notification service interface"""

    @abstractmethod
    async def send_push_notification(
        self, user_id: int, title: str, message: str
    ) -> bool:
        pass

    @abstractmethod
    async def send_sms(self, phone_number: str, message: str) -> bool:
        pass


class ISafetyService(ABC):
    """Safety and moderation service interface"""

    @abstractmethod
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def report_user(
        self, reporter_id: int, reported_user_id: int, reason: str
    ) -> bool:
        pass

    @abstractmethod
    async def block_user(self, user_id: int, blocked_user_id: int) -> bool:
        pass


# Type stubs for services
class DatabaseEngine:
    """Database engine type stub"""

    pass


class DatabaseSession:
    """Database session type stub"""

    pass


class RedisClient:
    """Redis client type stub"""

    pass


class VectorDBClient:
    """Vector DB client type stub"""

    pass


class Logger:
    """Logger type stub"""

    pass


class MonitoringService:
    """Monitoring service type stub"""

    pass


class RequestContext:
    """Request context type stub"""

    pass


class UserSession:
    """User session type stub"""

    pass


# Service Factory Patterns
class RepositoryFactory:
    """Factory for creating repository instances"""

    def __init__(self, container: ServiceContainer):
        self.container = container

    def create_user_repository(self) -> IUserRepository:
        """Create user repository instance"""
        from app.repositories.user_repository import UserRepository

        # Create a scope to get scoped services
        scope = self.container.create_scope()
        return UserRepository(
            db_session=scope.get_service(DatabaseSession),
            cache_manager=self.container.get_service(
                ICacheManager
            ),  # This is singleton
        )

    def create_challenge_repository(self) -> IChallengeRepository:
        """Create challenge repository instance"""
        from app.repositories.challenge_repository import ChallengeRepository

        return ChallengeRepository(
            db_session=self.container.get_service(DatabaseSession),
            cache_manager=self.container.get_service(ICacheManager),
        )


class MLServiceFactory:
    """Factory for creating ML service instances"""

    def __init__(self, container: ServiceContainer):
        self.container = container
        self.config = get_ml_config()

    def create_recommendation_service(self) -> IRecommendationService:
        """Create ML recommendation service instance"""
        from app.services.ml.recommendation_service import MLRecommendationService

        return MLRecommendationService(
            vector_db_client=self.container.get_service(VectorDBClient),
            openai_client=self.container.get_service(Logger),  # Placeholder
            embedding_service=self.container.get_service(IEmbeddingService),
        )

    def create_embedding_service(self) -> IEmbeddingService:
        """Create user embedding service instance"""
        from app.services.ml.embedding_service import UserEmbeddingService

        return UserEmbeddingService(
            vector_db_client=self.container.get_service(VectorDBClient),
            config=self.config,
        )

    def create_moderation_service(self) -> ISafetyService:
        """Create ML moderation service instance"""
        from app.services.ml.moderation_service import MLModerationService

        return MLModerationService(
            openai_client=self.container.get_service(Logger),  # Placeholder
            config=self.config,
        )


class ExternalServiceFactory:
    """Factory for creating external service instances"""

    def __init__(self, container: ServiceContainer):
        self.container = container
        self.config = get_config()

    def create_email_service(self) -> IEmailService:
        """Create email service instance"""
        from app.services.external.email_service import EmailService

        return EmailService(
            config=self.config.get_external_services_config(),
            logger=self.container.get_service(Logger),
        )

    def create_storage_service(self) -> IStorageService:
        """Create file storage service instance"""
        from app.services.external.storage_service import S3StorageService

        return S3StorageService(
            config=self.config.get_external_services_config(),
            logger=self.container.get_service(Logger),
        )

    def create_notification_service(self) -> INotificationService:
        """Create notification service instance"""
        from app.services.external.notification_service import NotificationService

        return NotificationService(
            config=self.config.get_external_services_config(),
            logger=self.container.get_service(Logger),
        )


# Service Registration Functions
def create_cache_manager_factory(redis_client: RedisClient) -> ICacheManager:
    """Factory function to create cache manager"""
    from app.services.cache.redis_cache_manager import RedisCacheManager

    return RedisCacheManager(redis_client)


def register_singleton_services(container: ServiceContainer):
    """Register singleton services (Database Engine, Redis Client, Vector DB Client)"""
    logger.info("Registering singleton services")

    # Database Engine
    container.register_singleton(DatabaseEngine, factory=create_database_engine)

    # Redis Client
    container.register_singleton(RedisClient, factory=create_redis_client)

    # Vector DB Client
    container.register_singleton(VectorDBClient, factory=create_vector_db_client)

    # Cache Manager
    container.register_singleton(ICacheManager, factory=create_cache_manager_factory)

    # Logging Provider
    container.register_singleton(Logger, factory=create_logger)

    # Monitoring Provider
    container.register_singleton(MonitoringService, factory=create_monitoring_service)


def register_scoped_services(container: ServiceContainer):
    """Register scoped services (Database Session, Request Context, User Session)"""
    logger.info("Registering scoped services")

    # Database Session
    container.register_scoped(DatabaseSession, factory=create_database_session_factory)

    # Request Context
    container.register_scoped(RequestContext, factory=lambda: create_request_context())

    # User Session
    container.register_scoped(UserSession, factory=lambda: create_user_session())


def create_user_repository_factory(factory: RepositoryFactory) -> IUserRepository:
    """Factory function to create user repository"""
    return factory.create_user_repository()


def create_challenge_repository_factory(
    factory: RepositoryFactory,
) -> IChallengeRepository:
    """Factory function to create challenge repository"""
    return factory.create_challenge_repository()


def create_repository_factory_factory(container: ServiceContainer) -> RepositoryFactory:
    """Factory function to create repository factory"""
    return RepositoryFactory(container)


def create_ml_service_factory_factory(container: ServiceContainer) -> MLServiceFactory:
    """Factory function to create ML service factory"""
    return MLServiceFactory(container)


def create_external_service_factory_factory(
    container: ServiceContainer,
) -> ExternalServiceFactory:
    """Factory function to create external service factory"""
    return ExternalServiceFactory(container)


def register_transient_services(container: ServiceContainer):
    """Register transient services (Repositories, Business Services, ML Services)"""
    logger.info("Registering transient services")

    # Repository Factory
    container.register_transient(
        RepositoryFactory, factory=lambda: RepositoryFactory(container)
    )

    # ML Service Factory
    container.register_transient(
        MLServiceFactory, factory=lambda: MLServiceFactory(container)
    )

    # External Service Factory
    container.register_transient(
        ExternalServiceFactory, factory=lambda: ExternalServiceFactory(container)
    )

    # Repositories
    container.register_transient(
        IUserRepository, factory=create_user_repository_factory
    )

    container.register_transient(
        IChallengeRepository, factory=create_challenge_repository_factory
    )

    # Business Services
    container.register_transient(
        IAuthService,
        factory=lambda user_repo, cache_manager, email_service: create_auth_service(
            user_repo, cache_manager, email_service
        ),
    )

    container.register_transient(
        IChallengeService,
        factory=lambda challenge_repo,
        ml_service,
        notification_service: create_challenge_service(
            challenge_repo, ml_service, notification_service
        ),
    )

    # ML Services
    container.register_transient(
        IRecommendationService,
        factory=lambda factory: factory.create_recommendation_service(),
    )

    container.register_transient(
        IEmbeddingService, factory=lambda factory: factory.create_embedding_service()
    )

    container.register_transient(
        ISafetyService, factory=lambda factory: factory.create_moderation_service()
    )

    # External Services
    container.register_transient(
        IEmailService, factory=lambda factory: factory.create_email_service()
    )

    container.register_transient(
        IStorageService, factory=lambda factory: factory.create_storage_service()
    )

    container.register_transient(
        INotificationService,
        factory=lambda factory: factory.create_notification_service(),
    )


def register_interface_bindings(container: ServiceContainer):
    """Register interface bindings"""
    logger.info("Registering interface bindings")

    # Repository Interfaces
    container.register_transient(IUserRepository, Any)  # UserRepository
    container.register_transient(IChallengeRepository, Any)  # ChallengeRepository

    # Service Interfaces
    container.register_transient(IAuthService, Any)  # AuthService
    container.register_transient(IChallengeService, Any)  # ChallengeService

    # ML Interfaces
    container.register_transient(IRecommendationService, Any)  # MLRecommendationService
    container.register_transient(IEmbeddingService, Any)  # UserEmbeddingService

    # External Interfaces
    container.register_transient(IEmailService, Any)  # EmailService
    container.register_transient(IStorageService, Any)  # S3StorageService


# Factory Functions
def create_database_engine():
    """Create database engine instance"""
    from sqlalchemy import create_engine
    from app.core.config import get_database_config

    config = get_database_config()
    return create_engine(
        config.url,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        echo=config.echo,
    )


def create_redis_client():
    """Create Redis client instance"""
    import redis
    from app.core.config import get_redis_config

    config = get_redis_config()
    return redis.Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        password=config.password,
        ssl=config.ssl,
        socket_timeout=config.socket_timeout,
        socket_connect_timeout=config.socket_connect_timeout,
        max_connections=config.max_connections,
    )


def create_vector_db_client():
    """Create vector database client instance"""
    from app.core.config import get_ml_config

    config = get_ml_config()
    if not config.vector_db_url:
        logger.warning("Vector DB URL not configured, using mock client")
        return MockVectorDBClient()

    # Initialize actual vector DB client (e.g., Pinecone, Weaviate)
    return VectorDBClient(config.vector_db_url, config.vector_db_api_key)


def create_cache_manager(redis_client):
    """Create cache manager instance"""
    from app.services.cache.redis_cache_manager import RedisCacheManager

    return RedisCacheManager(redis_client)


def create_logger():
    """Create logger instance"""
    from app.core.config import get_logging_config

    config = get_logging_config()
    logging.basicConfig(level=getattr(logging, config.level), format=config.format)
    return logging.getLogger(__name__)


def create_monitoring_service():
    """Create monitoring service instance"""
    from app.services.monitoring.monitoring_service import MonitoringService
    from app.core.config import get_monitoring_config

    config = get_monitoring_config()
    return MonitoringService(config)


def create_database_session_factory(db_engine: DatabaseEngine) -> DatabaseSession:
    """Factory function to create database session"""
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    return SessionLocal()


def create_request_context():
    """Create request context instance"""
    from app.core.request_context import RequestContext

    return RequestContext()


def create_user_session():
    """Create user session instance"""
    from app.core.user_session import UserSession

    return UserSession()


def create_auth_service(
    user_repo: IUserRepository,
    cache_manager: ICacheManager,
    email_service: IEmailService,
):
    """Create authentication service instance"""
    from app.services.auth_service import AuthService
    from app.core.config import get_security_config

    config = get_security_config()
    return AuthService(user_repo, cache_manager, email_service, config)


def create_challenge_service(
    challenge_repo: IChallengeRepository,
    ml_service: IRecommendationService,
    notification_service: INotificationService,
):
    """Create challenge service instance"""
    from app.services.challenge_service import ChallengeService

    return ChallengeService(challenge_repo, ml_service, notification_service)


# Mock implementations for development
class MockVectorDBClient:
    """Mock vector database client for development"""

    def __init__(self):
        self.vectors = {}

    async def upsert(self, namespace: str, vectors: List[Dict[str, Any]]):
        """Mock upsert operation"""
        for vector in vectors:
            self.vectors[vector["id"]] = vector

    async def query(self, namespace: str, vector: List[float], top_k: int = 10):
        """Mock query operation"""
        return [{"id": "mock_id", "score": 0.9}]


class VectorDBClient:
    """Real vector database client implementation"""

    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.api_key = api_key
        # Initialize actual vector DB client here

    async def upsert(self, namespace: str, vectors: List[Dict[str, Any]]):
        """Upsert vectors to database"""
        # Implement actual upsert logic
        pass

    async def query(self, namespace: str, vector: List[float], top_k: int = 10):
        """Query similar vectors"""
        # Implement actual query logic
        pass


# Service registration decorator
def register_service(
    service_type: Type[T], lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
):
    """Decorator to register a service"""

    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()

        if lifetime == ServiceLifetime.SINGLETON:
            container.register_singleton(service_type, cls)
        elif lifetime == ServiceLifetime.SCOPED:
            container.register_scoped(service_type, cls)
        else:
            container.register_transient(service_type, cls)

        return cls

    return decorator


# Main registration function
def register_all_services(container: ServiceContainer):
    """Register all services in the container"""
    logger.info("Starting service registration")

    # Register services by lifetime
    register_singleton_services(container)
    register_scoped_services(container)
    register_transient_services(container)

    # Note: Interface bindings are handled in the transient services section
    # register_interface_bindings(container)

    logger.info("Service registration completed")
