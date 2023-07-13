from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from avilla.core.account import AccountStatus, BaseAccount, AccountInfo
from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.core.platform import Abstract, Branch, Land, Platform, Version
from avilla.standard.core.account import AccountAvailable, AccountUnavailable

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol

platform = Platform(
    Land(
        "console",
        [{"name": "GraiaxCommunity"}],
        humanized_name="Avilla-Console - Console Impl for avilla",
    ),
    Abstract(
        protocol="Console",
        maintainers=[{"name": "yanyongyu"}],
        humanized_name="Textual Console",
    )
)

class ConsoleAccount(BaseAccount):
    protocol: ConsoleProtocol
    status: AccountStatus

    def __init__(self, protocol: ConsoleProtocol):
        super().__init__(Selector().land("console").account("user"), protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()
        self.protocol.avilla.accounts[self.route] = AccountInfo(
            self.route, self, self.protocol, platform
        )

    @contextmanager
    def _status_update(self):
        prev = self.available
        yield
        if prev != (curr := self.available):
            avilla = self.protocol.avilla
            avilla.broadcast.postEvent((AccountAvailable if curr else AccountUnavailable)(avilla, self))

    async def get_context(self, target: Selector, *, via: Selector | None = None) -> Context:
        if "land" not in target:
            target = target.land(self.route["land"])
        if target.path == "land.console":
            return Context(self, target, target, self.route.into("::"), self.route)
        else:
            raise NotImplementedError()

    @property
    def client(self):
        return self.protocol.service.app
    async def call(self, endpoint: str, params: dict[str, Any] | None = None):
        return await self.client.call(endpoint, params or {})

    @property
    def available(self) -> bool:
        return self.status.enabled
