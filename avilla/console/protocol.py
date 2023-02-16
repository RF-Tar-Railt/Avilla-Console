from __future__ import annotations

from typing import Awaitable, Callable

from avilla.console.account import ConsoleAccount
from avilla.console.service import ConsoleService
from avilla.core.application import Avilla
from avilla.core.context import Context
from avilla.core.event import AvillaEvent
from avilla.core.platform import Abstract, Land, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.trait.context import EventParse, wrap_artifacts

from graia.amnesia.message import __message_chain_class__
from graia.amnesia.message.element import Element, Text
from graia.amnesia.builtins.memcache import MemcacheService
from loguru import logger
from typing_extensions import TypeAlias
from .frontend.info import Event as ConsoleEvent
from .message import ConsoleMessage, Text as RichText, ConsoleElement

EventParser: TypeAlias = (
    "Callable[[ConsoleProtocol, ConsoleAccount, ConsoleEvent], Awaitable[tuple[AvillaEvent, Context]]]"
)


class ConsoleProtocol(BaseProtocol):
    platform = Platform(
        Land(
            "avilla-console",
            [{"name": "GraiaxCommunity"}],
            humanized_name="Avilla-Console - Console Impl for avilla",
        ),
        Abstract(
            protocol="Console",
            maintainers=[{"name": "yanyongyu"}],
            humanized_name="Textual Console",
        )
    )

    with wrap_artifacts() as implementations:
        import avilla.console.impl as _  # noqa
        import avilla.console.impl.console as _  # noqa

    with wrap_artifacts() as event_parsers:
        import avilla.console.event.message as _  # noqa

    with wrap_artifacts() as context_sources:
        import avilla.console.impl.context_source as _  # noqa

    service: ConsoleService

    def __init__(self):
        super().__init__()

    def ensure(self, avilla: Avilla):
        self.avilla = avilla
        self.service = ConsoleService(self)
        avilla.launch_manager.add_service(MemcacheService(1))
        avilla.launch_manager.add_service(self.service)

    async def serialize_message(
        self,
        message: __message_chain_class__,
        context: Context | None = None
    ) -> list[ConsoleElement]:
        result = []
        for element in message.content:
            if isinstance(element, Text):
                result.append(RichText(element.text))
            else:
                result.append(element)
        return result

    async def deserialize_message(self, context: Context, message: ConsoleMessage):
        serialized: list[Element] = []
        for raw_element in message:
            if isinstance(raw_element, RichText):
                serialized.append(Text(raw_element.text))
            else:
                serialized.append(raw_element)
        return serialized

    async def parse_event(
        self, account: ConsoleAccount, event: ConsoleEvent, *, error: bool = False
    ):
        if not hasattr(event, "type"):
            raise KeyError(f'expected "type" exists for {event}')
        event_type = event.type
        parser: EventParser | None = self.event_parsers.get(EventParse(event_type))
        if parser is None:
            if error:
                raise NotImplementedError(
                    f'expected event "{event_type}" implemented for {event}'
                )
            logger.warning(
                f"Event type {event_type} is not supported by {self.__class__.__name__}",
                event,
            )
            return
        return await parser(self, account, event)
