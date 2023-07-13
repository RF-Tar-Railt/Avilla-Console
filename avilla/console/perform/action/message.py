from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.message import Message
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend
from graia.amnesia.message import MessageChain
from loguru import logger
from ...frontend.info import Robot
from ...staff import ConsoleStaff

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleMessageActionPerform((m := ContextCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    @MessageSend.send.collect(m, "land.console")
    async def send_console_message(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(self.protocol, ConsoleProtocol)
        serialized_msg = await ConsoleStaff(self.account).serialize_message(message)

        await self.account.call(
            "send_msg",
            {
                "message": serialized_msg,
                "info": Robot("console")
            }
        )
        logger.info(  # TODO: wait for solution of ActiveMessage
            f"{self.account.route['land']}: [send]"
            f"[Console]"
            f" <- {str(message)!r}"
        )
        message_metadata = Message(
            id=str(datetime.now().timestamp()),
            scene=Selector().land(self.account.route["land"]).console(str(target.pattern["console"])),
            content=message,
            time=datetime.now(),
            sender=self.account.route,
        )
        return message_metadata.to_selector()