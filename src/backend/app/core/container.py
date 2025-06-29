"""
Dependency Injection Container for Pulse Fitness
Manages service registration, lifetime management, and dependency resolution
"""

import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from enum import Enum
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime enumeration"""

    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


class ServiceDescriptor:
    """Describes a service registration"""

    def __init__(
        self,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        factory: Optional[Callable] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        instance: Optional[Any] = None,
    ):
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.factory = factory
        self.lifetime = lifetime
        self.instance = instance
        self._async_factory = None

        # Check if factory is async
        if factory and inspect.iscoroutinefunction(factory):
            self._async_factory = factory


class ServiceProvider:
    """Service provider for dependency resolution"""

    def __init__(self, container: "ServiceContainer"):
        self.container = container
        self._scoped_instances: Dict[Type, Any] = {}
        self._disposables: List[Any] = []

    def get_service(self, service_type: Type[T]) -> T:
        """Get service instance"""
        return self.container._resolve_service(service_type, self)

    def get_required_service(self, service_type: Type[T]) -> T:
        """Get required service instance, raises if not found"""
        service = self.get_service(service_type)
        if service is None:
            raise ValueError(f"Service of type {service_type} not registered")
        return service

    async def get_service_async(self, service_type: Type[T]) -> T:
        """Get service instance asynchronously"""
        return await self.container._resolve_service_async(service_type, self)

    def create_scope(self) -> "ServiceProvider":
        """Create a new scoped service provider"""
        return ServiceProvider(self.container)


class ServiceContainer:
    """Main dependency injection container"""

    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singleton_instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._async_factories: Dict[Type, Callable] = {}
        self._disposables: List[Any] = []
        self._is_disposed = False

    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "ServiceContainer":
        """Register a singleton service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.SINGLETON,
        )
        self._services[service_type] = descriptor
        return self

    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "ServiceContainer":
        """Register a scoped service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.SCOPED,
        )
        self._services[service_type] = descriptor
        return self

    def register_transient(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> "ServiceContainer":
        """Register a transient service"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=ServiceLifetime.TRANSIENT,
        )
        self._services[service_type] = descriptor
        return self

    def register_instance(
        self, service_type: Type[T], instance: T
    ) -> "ServiceContainer":
        """Register a singleton instance"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance,
        )
        self._services[service_type] = descriptor
        self._singleton_instances[service_type] = instance
        return self

    def create_scope(self) -> ServiceProvider:
        """Create a new service scope"""
        return ServiceProvider(self)

    def get_service(self, service_type: Type[T]) -> T:
        """Get service from root container (singleton only)"""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")

        descriptor = self._services[service_type]
        if descriptor.lifetime != ServiceLifetime.SINGLETON:
            raise ValueError(f"Service {service_type} is not singleton")

        return self._resolve_service(service_type, None)

    def _resolve_service(
        self, service_type: Type[T], provider: Optional[ServiceProvider]
    ) -> T:
        """Resolve service instance"""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")

        descriptor = self._services[service_type]

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singleton_instances:
                return self._singleton_instances[service_type]

            instance = self._create_instance(descriptor, provider)
            self._singleton_instances[service_type] = instance
            return instance

        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if provider and service_type in provider._scoped_instances:
                return provider._scoped_instances[service_type]

            instance = self._create_instance(descriptor, provider)
            if provider:
                provider._scoped_instances[service_type] = instance
            return instance

        else:  # TRANSIENT
            return self._create_instance(descriptor, provider)

    async def _resolve_service_async(
        self, service_type: Type[T], provider: Optional[ServiceProvider]
    ) -> T:
        """Resolve service instance asynchronously"""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")

        descriptor = self._services[service_type]

        # Handle different lifetimes
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singleton_instances:
                return self._singleton_instances[service_type]

            instance = await self._create_instance_async(descriptor, provider)
            self._singleton_instances[service_type] = instance
            return instance

        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if provider and service_type in provider._scoped_instances:
                return provider._scoped_instances[service_type]

            instance = await self._create_instance_async(descriptor, provider)
            if provider:
                provider._scoped_instances[service_type] = instance
            return instance

        else:  # TRANSIENT
            return await self._create_instance_async(descriptor, provider)

    def _create_instance(
        self, descriptor: ServiceDescriptor, provider: Optional[ServiceProvider]
    ) -> Any:
        """Create service instance"""
        if descriptor.instance is not None:
            return descriptor.instance

        if descriptor.factory:
            if descriptor._async_factory:
                raise ValueError(
                    f"Async factory {descriptor.factory} cannot be used in sync context"
                )
            return self._invoke_factory(descriptor.factory, provider)

        implementation_type = descriptor.implementation_type or descriptor.service_type
        return self._create_instance_from_type(implementation_type, provider)

    async def _create_instance_async(
        self, descriptor: ServiceDescriptor, provider: Optional[ServiceProvider]
    ) -> Any:
        """Create service instance asynchronously"""
        if descriptor.instance is not None:
            return descriptor.instance

        if descriptor.factory:
            if descriptor._async_factory:
                return await self._invoke_factory_async(descriptor.factory, provider)
            else:
                return self._invoke_factory(descriptor.factory, provider)

        implementation_type = descriptor.implementation_type or descriptor.service_type
        return await self._create_instance_from_type_async(
            implementation_type, provider
        )

    def _create_instance_from_type(
        self, implementation_type: Type, provider: Optional[ServiceProvider]
    ) -> Any:
        """Create instance from type with dependency injection"""
        if not inspect.isclass(implementation_type):
            raise ValueError(f"{implementation_type} is not a class")

        # Get constructor parameters
        sig = inspect.signature(implementation_type.__init__)
        params = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.annotation == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter {name} in {implementation_type} has no type annotation"
                )

            # Resolve dependency
            if provider:
                params[name] = provider.get_service(param.annotation)
            else:
                params[name] = self.get_service(param.annotation)

        return implementation_type(**params)

    async def _create_instance_from_type_async(
        self, implementation_type: Type, provider: Optional[ServiceProvider]
    ) -> Any:
        """Create instance from type asynchronously"""
        if not inspect.isclass(implementation_type):
            raise ValueError(f"{implementation_type} is not a class")

        # Get constructor parameters
        sig = inspect.signature(implementation_type.__init__)
        params = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue

            if param.annotation == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter {name} in {implementation_type} has no type annotation"
                )

            # Resolve dependency
            if provider:
                params[name] = await provider.get_service_async(param.annotation)
            else:
                params[name] = await self._resolve_service_async(
                    param.annotation, provider
                )

        return implementation_type(**params)

    def _invoke_factory(
        self, factory: Callable, provider: Optional[ServiceProvider]
    ) -> Any:
        """Invoke factory function with dependency injection"""
        sig = inspect.signature(factory)
        params = {}

        for name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                raise ValueError(f"Factory parameter {name} has no type annotation")

            if provider:
                params[name] = provider.get_service(param.annotation)
            else:
                params[name] = self.get_service(param.annotation)

        return factory(**params)

    async def _invoke_factory_async(
        self, factory: Callable, provider: Optional[ServiceProvider]
    ) -> Any:
        """Invoke async factory function with dependency injection"""
        sig = inspect.signature(factory)
        params = {}

        for name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                raise ValueError(f"Factory parameter {name} has no type annotation")

            if provider:
                params[name] = await provider.get_service_async(param.annotation)
            else:
                params[name] = await self._resolve_service_async(
                    param.annotation, provider
                )

        return await factory(**params)

    def dispose(self):
        """Dispose the container and all disposable services"""
        if self._is_disposed:
            return

        self._is_disposed = True

        # Dispose all disposable services
        for instance in self._singleton_instances.values():
            if hasattr(instance, "dispose"):
                instance.dispose()

        for disposable in self._disposables:
            if hasattr(disposable, "dispose"):
                disposable.dispose()

        logger.info("Service container disposed")


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def configure_services(configure: Callable[[ServiceContainer], None]):
    """Configure services in the global container"""
    container = get_container()
    configure(container)
    return container


@asynccontextmanager
async def create_scope():
    """Create a service scope context manager"""
    container = get_container()
    scope = container.create_scope()
    try:
        yield scope
    finally:
        # Clean up scoped instances
        scope._scoped_instances.clear()
        scope._disposables.clear()
