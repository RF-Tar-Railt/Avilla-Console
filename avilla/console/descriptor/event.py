from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from avilla.core._vendor.dataclasses import dataclass
from avilla.core.ryanvk.descriptor.event import EventParserSign
from avilla.console.frontend.info import Event as ConsoleEvent

if TYPE_CHECKING:
    from avilla.core.event import AvillaEvent
    from avilla.standard.core.account.event import AvillaLifecycleEvent

    from avilla.core.ryanvk.collector.base import BaseCollector, PerformTemplate

M = TypeVar("M", bound="PerformTemplate", contravariant=True)


class ConsoleEventParse:
    @classmethod
    def collect(cls, collector: BaseCollector, event_type: str):
        def receiver(entity: Callable[[M, ConsoleEvent], Awaitable[AvillaEvent | AvillaLifecycleEvent | None]]):
            collector.artifacts[EventParserSign(event_type)] = (collector, entity)
            return entity

        return receiver
