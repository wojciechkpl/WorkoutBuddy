import pytest
from app.core.container import ServiceContainer, ServiceLifetime


class DummySingleton:
    def __init__(self):
        pass


class DummyScoped:
    def __init__(self):
        pass


class DummyTransient:
    def __init__(self):
        pass


def test_singleton_lifetime():
    container = ServiceContainer()
    container.register_singleton(DummySingleton)
    a = container.get_service(DummySingleton)
    b = container.get_service(DummySingleton)
    assert a is b


def test_scoped_lifetime():
    container = ServiceContainer()
    container.register_scoped(DummyScoped)
    scope1 = container.create_scope()
    scope2 = container.create_scope()
    a = scope1.get_service(DummyScoped)
    b = scope1.get_service(DummyScoped)
    c = scope2.get_service(DummyScoped)
    assert a is b
    assert a is not c


def test_transient_lifetime():
    container = ServiceContainer()
    container.register_transient(DummyTransient)
    scope = container.create_scope()
    a = scope.get_service(DummyTransient)
    b = scope.get_service(DummyTransient)
    assert a is not b


def test_dependency_resolution():
    class Dep:
        def __init__(self):
            pass

    class Service:
        def __init__(self, dep: Dep):
            self.dep = dep

    container = ServiceContainer()
    container.register_singleton(Dep)
    container.register_transient(Service)
    scope = container.create_scope()
    service = scope.get_service(Service)
    assert isinstance(service, Service)
    assert isinstance(service.dep, Dep)
