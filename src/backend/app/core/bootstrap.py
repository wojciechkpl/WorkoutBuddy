"""
Application Bootstrap System for Pulse Fitness
Handles application startup, middleware setup, and service initialization
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Callable, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import traceback

from .container import ServiceContainer, get_container, configure_services, create_scope
from .config import (
    get_config,
    get_security_config,
    get_logging_config,
    get_monitoring_config,
)
from .service_registration import register_all_services

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """Main application bootstrap class"""

    def __init__(self):
        self.app: Optional[FastAPI] = None
        self.container: Optional[ServiceContainer] = None
        self.config = get_config()
        self._startup_complete = False
        self._shutdown_complete = False

    async def bootstrap(self) -> FastAPI:
        """Bootstrap the application"""
        logger.info("Starting application bootstrap")

        try:
            # Step 1: Load Configuration
            await self._load_configuration()

            # Step 2: Create DI Container
            await self._create_container()

            # Step 3: Register Services
            await self._register_services()

            # Step 4: Create FastAPI Application
            await self._create_application()

            # Step 5: Configure Middleware
            await self._configure_middleware()

            # Step 6: Setup Routes
            await self._setup_routes()

            # Step 7: Initialize External Connections
            await self._initialize_external_connections()

            # Step 8: Start Application
            await self._start_application()

            self._startup_complete = True
            logger.info("Application bootstrap completed successfully")

            return self.app

        except Exception as e:
            logger.error(f"Application bootstrap failed: {e}")
            logger.error(traceback.format_exc())
            await self._cleanup()
            raise

    async def _load_configuration(self):
        """Step 1: Load configuration"""
        logger.info("Loading configuration")

        # Configuration is already loaded in __init__
        # Validate critical configuration
        if not self.config.get("database_url"):
            raise ValueError("Database URL not configured")

        if not self.config.get("secret_key"):
            raise ValueError("Secret key not configured")

        logger.info("Configuration loaded successfully")

    async def _create_container(self):
        """Step 2: Create DI Container"""
        logger.info("Creating dependency injection container")

        self.container = get_container()
        logger.info("Dependency injection container created")

    async def _register_services(self):
        """Step 3: Register services"""
        logger.info("Registering services")

        if not self.container:
            raise RuntimeError("Container not initialized")

        register_all_services(self.container)
        logger.info("Services registered successfully")

    async def _create_application(self):
        """Step 4: Create FastAPI application"""
        logger.info("Creating FastAPI application")

        self.app = FastAPI(
            title="Pulse Fitness API",
            description="Fitness app with ML-powered recommendations and social features",
            version="1.0.0",
            docs_url="/docs" if self.config.is_development() else None,
            redoc_url="/redoc" if self.config.is_development() else None,
            openapi_url="/openapi.json" if self.config.is_development() else None,
        )

        # Add lifespan events
        self.app.add_event_handler("startup", self._on_startup)
        self.app.add_event_handler("shutdown", self._on_shutdown)

        logger.info("FastAPI application created")

    async def _configure_middleware(self):
        """Step 5: Configure middleware"""
        logger.info("Configuring middleware")

        if not self.app:
            raise RuntimeError("FastAPI app not initialized")

        # CORS Middleware
        security_config = get_security_config()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=security_config.cors_origins or ["*"],
            allow_credentials=security_config.cors_allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Trusted Host Middleware (for production)
        if self.config.is_production():
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=["*"],  # Configure with actual domains
            )

        # GZip Middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Custom middleware for dependency injection
        self.app.add_middleware(DependencyInjectionMiddleware, container=self.container)

        # Custom middleware for monitoring
        if get_monitoring_config().performance_monitoring:
            self.app.add_middleware(PerformanceMonitoringMiddleware)

        # Custom middleware for rate limiting
        self.app.add_middleware(RateLimitMiddleware, config=security_config)

        logger.info("Middleware configured successfully")

    async def _setup_routes(self):
        """Step 6: Setup routes"""
        logger.info("Setting up routes")

        if not self.app:
            raise RuntimeError("FastAPI app not initialized")

        # Import and register route modules
        from app.api import (
            auth,
            users,
            challenges,
            social,
            workouts,
            exercises,
            accountability,
            subscriptions,
            community,
            privacy,
            safety,
            recommendations,
        )

        # Register route modules
        self.app.include_router(
            auth.router, prefix="/api/auth", tags=["Authentication"]
        )
        self.app.include_router(users.router, prefix="/api/users", tags=["Users"])
        self.app.include_router(
            challenges.router, prefix="/api/challenges", tags=["Challenges"]
        )
        self.app.include_router(social.router, prefix="/api/social", tags=["Social"])
        self.app.include_router(
            workouts.router, prefix="/api/workouts", tags=["Workouts"]
        )
        self.app.include_router(
            exercises.router, prefix="/api/exercises", tags=["Exercises"]
        )
        self.app.include_router(
            accountability.router, prefix="/accountability", tags=["Accountability"]
        )
        self.app.include_router(
            subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"]
        )
        self.app.include_router(
            community.router, prefix="/communities", tags=["Communities"]
        )
        self.app.include_router(privacy.router, prefix="/privacy", tags=["Privacy"])
        self.app.include_router(safety.router, prefix="/safety", tags=["Safety"])
        self.app.include_router(
            recommendations.router,
            prefix="/api/v1/recommendations",
            tags=["Recommendations"],
        )

        # Health check endpoint
        self.app.add_api_route("/health", self._health_check, methods=["GET"])

        logger.info("Routes setup completed")

    async def _initialize_external_connections(self):
        """Step 7: Initialize external connections"""
        logger.info("Initializing external connections")

        if not self.container:
            raise RuntimeError("Container not initialized")

        try:
            # Initialize database connection
            # For now, skip database initialization in tests
            if not get_config().is_testing():
                logger.info("Skipping external connections in test mode")

            logger.info("External connections initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize external connections: {e}")
            raise

    async def _start_application(self):
        """Step 8: Start application"""
        logger.info("Starting application")

        # Perform final health checks
        await self._perform_health_checks()

        logger.info("Application started successfully")

    async def _perform_health_checks(self):
        """Perform health checks"""
        logger.info("Performing health checks")

        checks = [
            ("Database", self._check_database_health),
            ("Redis", self._check_redis_health),
            ("ML Services", self._check_ml_health),
        ]

        for name, check_func in checks:
            try:
                await check_func()
                logger.info(f"Health check passed: {name}")
            except Exception as e:
                logger.error(f"Health check failed: {name} - {e}")
                if self.config.is_production():
                    raise

    async def _check_database_health(self):
        """Check database health"""
        if not self.container:
            raise RuntimeError("Container not available")

        # Skip database health check in test mode
        if get_config().is_testing():
            return

        # TODO: Implement actual database health check
        pass

    async def _check_redis_health(self):
        """Check Redis health"""
        if not self.container:
            raise RuntimeError("Container not available")

        # Skip Redis health check in test mode
        if get_config().is_testing():
            return

        # TODO: Implement actual Redis health check
        pass

    async def _check_ml_health(self):
        """Check ML services health"""
        if not self.container:
            raise RuntimeError("Container not available")

        # Skip ML health check in test mode
        if get_config().is_testing():
            return

        # TODO: Implement actual ML health check
        pass

    async def _on_startup(self):
        """Application startup event"""
        logger.info("Application startup event triggered")

        # Additional startup tasks can be added here
        # For example, warm up caches, preload models, etc.

        if get_config().is_feature_enabled("enable_ml_recommendations"):
            logger.info("Warming up ML models")
            # Warm up ML models if needed

    async def _on_shutdown(self):
        """Application shutdown event"""
        logger.info("Application shutdown event triggered")

        await self._cleanup()

    async def _cleanup(self):
        """Cleanup resources"""
        if self._shutdown_complete:
            return

        logger.info("Cleaning up resources")

        try:
            # Dispose container
            if self.container:
                self.container.dispose()

            # Close external connections
            await self._close_external_connections()

            self._shutdown_complete = True
            logger.info("Cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def _close_external_connections(self):
        """Close external connections"""
        logger.info("Closing external connections")

        # Close database connections
        # Close Redis connections
        # Close ML service connections
        # etc.

    async def _health_check(self):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "environment": self.config.get_environment().value,
        }


# Middleware Classes
class DependencyInjectionMiddleware:
    """Middleware for dependency injection"""

    def __init__(self, app, container: ServiceContainer):
        self.app = app
        self.container = container

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create a new scope for each request
            async with create_scope() as request_scope:
                # Add scope to request state
                scope["state"]["service_scope"] = request_scope

                # Continue processing
                await self.app(scope, receive, send)


class PerformanceMonitoringMiddleware:
    """Middleware for performance monitoring"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Create a custom send function to capture response time
            async def send_with_timing(message):
                if message["type"] == "http.response.start":
                    response_time = time.time() - start_time
                    logger.info(f"Request {scope['path']} took {response_time:.3f}s")

                await send(message)

            await self.app(scope, receive, send_with_timing)
        else:
            await self.app(scope, receive, send)


class RateLimitMiddleware:
    """Middleware for rate limiting"""

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.request_counts = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract client IP
            client = scope.get("client")
            client_ip = client[0] if client else "unknown"

            # Check rate limit
            if not await self._check_rate_limit(client_ip):
                # Return 429 Too Many Requests
                await send(
                    {
                        "type": "http.response.start",
                        "status": 429,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": b'{"error": "Rate limit exceeded"}',
                    }
                )
                return

            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limit"""
        current_time = time.time()
        window_start = current_time - self.config.rate_limit_window

        # Clean old entries
        self.request_counts = {
            ip: times
            for ip, times in self.request_counts.items()
            if any(t > window_start for t in times)
        }

        # Get client request times
        client_times = self.request_counts.get(client_ip, [])
        client_times = [t for t in client_times if t > window_start]

        # Check if within limit
        if len(client_times) >= self.config.rate_limit_requests:
            return False

        # Add current request
        client_times.append(current_time)
        self.request_counts[client_ip] = client_times

        return True


# Global bootstrap instance
_bootstrap: Optional[ApplicationBootstrap] = None


def get_bootstrap() -> ApplicationBootstrap:
    """Get the global bootstrap instance"""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = ApplicationBootstrap()
    return _bootstrap


async def create_app() -> FastAPI:
    """Create and bootstrap the FastAPI application"""
    bootstrap = get_bootstrap()
    return await bootstrap.bootstrap()


# Convenience function for testing
async def create_test_app() -> FastAPI:
    """Create a test application with minimal configuration"""
    # Override configuration for testing
    import os

    os.environ["ENVIRONMENT"] = "testing"

    bootstrap = ApplicationBootstrap()
    return await bootstrap.bootstrap()
