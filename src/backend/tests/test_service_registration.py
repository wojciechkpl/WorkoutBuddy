import pytest
from app.core.service_registration import (
    IUserRepository,
    IAuthService,
    RepositoryFactory,
    register_all_services,
)
from app.core.container import ServiceContainer


def test_register_all_services():
    container = ServiceContainer()
    register_all_services(container)
    # Should be able to resolve core interfaces from a scope
    scope = container.create_scope()
    repo = scope.get_service(IUserRepository)
    assert repo is not None
    # Should be able to resolve factories
    factory = scope.get_service(RepositoryFactory)
    assert isinstance(factory, RepositoryFactory)


def test_factory_produces_repository():
    container = ServiceContainer()
    register_all_services(container)
    scope = container.create_scope()
    factory = scope.get_service(RepositoryFactory)
    repo = factory.create_user_repository()
    assert repo is not None
