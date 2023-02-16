from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Set, Literal
from launart import Launart, Service, ExportInterface
from .frontend import Frontend
from .message import ConsoleMessage, Text

if TYPE_CHECKING:
    from .protocol import ConsoleProtocol


class ConsoleInterface(ExportInterface["ConsoleService"]):
    def __init__(self, service: ConsoleService):
        self.service = service

    def send(self, content: str):
        from .frontend.info import Robot
        self.service.app.call(
            "send_msg",
            {
                "message": ConsoleMessage([Text(content)]),
                "info": Robot("console")
            }
        )


class ConsoleService(Service):
    id = "console.service"
    supported_interface_types = {ConsoleInterface}

    protocol: ConsoleProtocol
    app: Frontend

    def __init__(self, protocol: ConsoleProtocol):
        self.protocol = protocol
        self.app = Frontend(protocol)
        super().__init__()

    def get_interface(self, interface_type) -> ConsoleInterface:
        return ConsoleInterface(self)

    @property
    def required(self):
        return {}

    @property
    def stages(self) -> Set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            ...

        async with self.stage("blocking"):
            task = asyncio.create_task(self.app.run_async())
            ...

        async with self.stage("cleanup"):
            self.app.exit()
            if task:
                await task
