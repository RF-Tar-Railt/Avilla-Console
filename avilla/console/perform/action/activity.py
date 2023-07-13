from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from avilla.core.message import Message
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger
from loguru import logger
from ...frontend.info import Robot
from ...staff import ConsoleStaff

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleActivityActionPerform((m := ContextCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    @ActivityTrigger.trigger.collect(m, "land.console")
    async def bell(self):
        await self.account.call("bell")