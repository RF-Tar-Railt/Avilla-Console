from __future__ import annotations

from typing import TYPE_CHECKING, Any
from avilla.core.account import AbstractAccount
from avilla.core.context import Context
from avilla.core.selector import Selector

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol


class ConsoleAccount(AbstractAccount):
    protocol: ConsoleProtocol

    def __init__(self, protocol: ConsoleProtocol):
        super().__init__("console", protocol)
        protocol.avilla.add_account(self)

    async def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        # TODO: 对象存在性检查
        if "land" not in target:
            target = target.land(self.protocol.land)
        if target.path == "land.console":
            return Context(self, target, target, self.to_selector(), self.to_selector())
        else:
            raise NotImplementedError()

    @property
    def client(self):
        return self.protocol.service.app

    @property
    def available(self) -> bool:
        return not self.client._exit

    async def call(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        return await self.client.call(endpoint, params or {})
