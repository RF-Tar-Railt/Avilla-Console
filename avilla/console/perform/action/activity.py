from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.standard.core.activity import ActivityTrigger


if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleActivityActionPerform((m := ContextCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    @ActivityTrigger.trigger.collect(m, "land.console")
    async def bell(self, target: Selector | None = None):
        await self.account.call("bell")