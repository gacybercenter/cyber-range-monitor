from __future__ import annotations

import abc
import time
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Callable, Generic, Iterable, TypeVar, Type
from typing_extensions import NamedTuple

from pydantic import BaseModel, ValidationError
from .exceptions import RuntimeValidationError

E = TypeVar('E', bound=StrEnum)

# Type alias: event handler receives validated kwargs and returns Any.
EventHandler = Callable[..., Any]
SchemaType = type[BaseModel] | None


class _EventProxies(NamedTuple, Generic[E]):
    registry: MappingProxyType[E, EventHandler]
    schemas: MappingProxyType[E, SchemaType]

class EventExistsError(Exception):
    def __init__(self, event: str) -> None:
        super().__init__(f'Event {event!s} already registered, and override is False')

class RegistryFrozenError(Exception):
    def __init__(self) -> None:
        super().__init__('Registry is frozen; cannot mutate EventRegistry')

class EventNotRegisteredError(Exception):
    def __init__(self, event: str, registered_events: list[str]) -> None:
        super().__init__(
            f'Cannot access event {event!s} when its not registered, '
            'registered events: {', '.join(registered_events)}'
        )

OnDecorator = Callable[[EventHandler], EventHandler]



class EventRegistryAdapter(Generic[E], abc.ABC):
    __slots__ = (
        '__registry',
        '__schemas',
        '__frozen',
    )

    def __init__(self) -> None:
        self.__registry: dict[E, EventHandler] = {}
        self.__schemas: dict[E, SchemaType] = {}
        self.__frozen: bool = False

    def has(self, event: E, *, schema: SchemaType | None = None) -> bool:
        base_clause = event in self.__registry
        if schema is not None:
            return base_clause and self.__schemas.get(event) is schema
        return base_clause

    def clear(self) -> None:
        self.__registry.clear()
        self.__schemas.clear()

    def _add_schema(self, event: E, schema: SchemaType) -> None:
        if self.__frozen:
            raise RegistryFrozenError()
        self.__schemas[event] = schema

    def build(self) -> _EventProxies[E]:
        if self.__frozen:
            return _EventProxies(
                registry=MappingProxyType(self.__registry),
                schemas=MappingProxyType(self.__schemas),
            )

        self.__frozen = True
        reg = MappingProxyType(dict(self.__registry))
        sch = MappingProxyType(dict(self.__schemas))
        self.__registry.clear()
        self.__schemas.clear()

        return _EventProxies(registry=reg, schemas=sch)

    def _add_event(
        self,
        event: E,
        handler: EventHandler,
        *,
        schema: SchemaType = None,
        override: bool = False
    ) -> None:
        if self.__frozen:
            raise RegistryFrozenError()

        if not override and event in self.__registry:
            raise EventExistsError(event=event)

        self.__registry[event] = handler
        self.__schemas[event] = schema


    @abc.abstractmethod
    def on(
        self,
        event: E,
        *,
        schema: SchemaType = None,
        override: bool = False,
    ):
        ...

    def off(self, event: E) -> None:
        if self.__frozen:
            raise RegistryFrozenError()
        self.__registry.pop(event, None)
        self.__schemas.pop(event, None)

class EventEmitterAdapter(Generic[E], abc.ABC):
    __slots__ = (
        '__registry',
        '__schemas',
    )
    def __init__(self, event_registry: EventRegistryAdapter[E]) -> None:
        proxies = event_registry.build()
        self.__registry: MappingProxyType[E, EventHandler] = proxies.registry
        self.__schemas: MappingProxyType[E, SchemaType] = proxies.schemas


    def get_event_handler(self, event: E) -> EventHandler:
        try:
            return self.__registry[event]
        except KeyError:
            raise EventNotRegisteredError(
                event=event,
                registered_events=list(self.__registry.keys()),
            )

    def get_event_schema(self, event: E, **kwargs) -> BaseModel | None:
        if not (event_schema := self.__schemas.get(event)):
            return None

        try:
            arguments = event_schema(**kwargs)
        except ValidationError as ve:
            raise RuntimeValidationError(ve) from ve

        return arguments

    @abc.abstractmethod
    def __call__(self, event: E, /, **kwargs: Any) -> Any: ...


class EventRegistry(Generic[E], EventRegistryAdapter[E]):
    __slots__ = ('_registry', '_schemas', '_frozen')

    def on(
        self,
        event: E,
        *,
        schema: SchemaType = None,
        override: bool = False
    ) -> OnDecorator:
        def _decorate(fn: EventHandler) -> EventHandler:
            self._add_event(
                event,
                fn,
                schema=schema,
                override=override,
            )
            return fn
        return _decorate




class EventRegistr(Generic[E]):
    __slots__ = ('_registry', '_schemas', '_frozen')

    def __init__(
        self,
        registry: dict[E, EventHandler],
        schemas: dict[E, SchemaType],
    ) -> None:
        self._registry: dict[E, EventHandler] = registry
        self._schemas: dict[E, SchemaType] = schemas
        self._frozen: bool = False

    def has(self, event: E, *, schema: SchemaType | None = None) -> bool:
        base_clause = event in self._registry
        if schema is not None:
            return base_clause and self._schemas.get(event) is schema
        return base_clause

    def clear(self) -> None:
        self._registry.clear()
        self._schemas.clear()

    def _as_mapping(self, dct: dict[Any, Any]) -> MappingProxyType[Any, Any]:
        return MappingProxyType(dict(dct))

    def build(self) -> _EventProxies[E]:
        proxies = _EventProxies(
            registry=self._as_mapping(self._registry),
            schemas=self._as_mapping(self._schemas),
        )
        self.clear()
        self._frozen = True
        return proxies

    def on(
        self,
        event: E,
        *,
        schema: SchemaType = None,
        override: bool = False,
    ) -> OnDecorator:
        def _decorate(fn: EventHandler) -> EventHandler:
            if self._frozen:
                raise RegistryFrozenError()

            if not override and event in self._registry:
                raise EventExistsError(event=event)

            self._registry[event] = fn
            self._schemas[event] = schema

            return fn
        return _decorate

    def off(self, event: E) -> None:
        if self._frozen:
            raise RegistryFrozenError()
        self._registry.pop(event, None)
        self._schemas.pop(event, None)

class EventEmitter(Generic[E]):

    __slots__ = ('_registry', '_schemas', '_observer')

    def __init__(self) -> None



class FrozenEmitter(Generic[E]):
    """
    Immutable, memory-efficient event dispatcher produced by EventEmitter.construct().
    """

    __slots__ = ('_registry', '_schemas', '_observer')

    def __init__(
        self,
        registry: MappingProxyType[E, EventHandler],
        schemas: MappingProxyType[E, SchemaType],
    ) -> None:
        self._registry: MappingProxyType[E, EventHandler] = registry
        self._schemas: MappingProxyType[E, SchemaType] = schemas

    def emit(self, event: E, /, **kwargs: Any) -> Any:
        try:
            handler = self._registry[event]
        except KeyError:
            raise RuntimeError(f'Event {event!s} not registered')

        schema = self._schemas.get(event)
        if schema is not None:
            try:
                model = schema(**kwargs)
                kwargs = model.model_dump()
            except ValidationError as ve:
                raise RuntimeValidationError(ve)

        return handler(**kwargs)


class EventEmitter(Generic[E]):
    """
    Builder-style event emitter.

    Usage:
        emitter = EventEmitter[MyEvent](observer=my_observer)

        @emitter.on(MyEvent.FOO, schema=FooArgs)
        def handle_foo(...):
            ...

        runtime = emitter.construct()   # freeze & get an immutable FrozenEmitter
        runtime.emit(MyEvent.FOO, ...)  # validated dispatch
    """

    __slots__ = ('_registry', '_schemas', '_frozen', '_observer')

    def __init__(
        self,
        *,
        observer: Callable[[E, float, BaseException | None], None] | None = None,
    ) -> None:
        self._registry: dict[E, EventHandler] = {}
        self._schemas: dict[E, SchemaType] = {}
        self._frozen: bool = False
        self._observer = observer

    def on(
        self,
        event: E,
        *,
        schema: SchemaType = None,
        replace: bool = False,
    ) -> Callable[[EventHandler], EventHandler]:
        """
        Instance decorator to register an event handler.
        Optionally attach a Pydantic schema to validate kwargs at emit-time.

        Example:
            @emitter.on(MyEvent.SAVE, schema=SaveArgs)
            def save_handler(...): ...
        """

        def _decorate(fn: EventHandler) -> EventHandler:
            if self._frozen:
                raise RuntimeError('Emitter is frozen; cannot register new handlers')
            if not replace and event in self._registry:
                raise RuntimeError(f'Event {event!s} already registered')
            self._registry[event] = fn
            self._schemas[event] = schema
            return fn

        return _decorate

    def off(self, event: E) -> None:
        if self._frozen:
            raise RuntimeError('Emitter is frozen; cannot unregister handlers')
        self._registry.pop(event, None)
        self._schemas.pop(event, None)

    def has(self, event: E) -> bool:
        return event in self._registry

    def require(self, *events: E) -> None:
        missing = [ev for ev in events if ev not in self._registry]
        if missing:
            raise RuntimeError(f'Missing handlers: {missing}')

    def construct(self) -> FrozenEmitter[E]:
        if self._frozen:
            return FrozenEmitter(
                registry=self._as_mapping(self._registry),
                schemas=self._as_mapping(self._schemas),
            )

        self._frozen = True
        # wrap dicts with MappingProxyType to prevent further mutation
        reg = MappingProxyType(dict(self._registry))
        sch = MappingProxyType(dict(self._schemas))
        # drop original dicts to allow GC to reclaim memory
        self._registry.clear()
        self._schemas.clear()

        return FrozenEmitter(registry=reg, schemas=sch)

    @staticmethod
    def _as_mapping(dct: dict[Any, Any]) -> MappingProxyType[Any, Any]:
        return MappingProxyType(dict(dct))


# =============================================================================
# Example: Adapting this to Redis later
# =============================================================================
# You can wire this into a RedisCommandAdapter by:
#
#   - Defining an enum of commands (StrEnum)
#   - Registering handlers that ACCEPT (pipe, **kwargs) and RETURN the pipe
#   - Using the FrozenEmitter at runtime to emit commands and build a pipeline
#
# Example sketch (handlers can be normal functions; they may close over config):
#
#   class Cmd(StrEnum):
#       SET = "set"
#       TOUCH = "touch"
#
#   from redis.asyncio import client as aioredis_client
#   from pydantic import BaseModel
#
#   class SetArgs(BaseModel):
#       key: str
#       payload: dict[str, Any]
#       ttl: int
#
#   emitter = EventEmitter[Cmd]()
#
#   @emitter.on(Cmd.SET, schema=SetArgs)
#   def set_cmd(*, pipe: aioredis_client.Pipeline, key: str, payload: dict[str, Any], ttl: int):
#       pipe.hset(key, mapping=payload)
#       pipe.expire(key, ttl)
#       return pipe
#
#   runtime = emitter.construct()
#
#   # Then:
#   # pipe = runtime.emit(Cmd.SET, pipe=pipe, key="sess:1", payload={...}, ttl=1800)
#
