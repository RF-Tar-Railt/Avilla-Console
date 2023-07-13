from __future__ import annotations

from typing import TYPE_CHECKING

from avilla.standard.core.profile import Summary, Nick
from avilla.core.ryanvk.collector.context import ContextCollector
from avilla.core.selector import Selector
from avilla.core.ryanvk.descriptor.pull import PullFn

if TYPE_CHECKING:
    from ...account import ConsoleAccount  # noqa
    from ...protocol import ConsoleProtocol  # noqa


class ConsoleProfileActionPerform((m := ContextCollector["ConsoleProtocol", "ConsoleAccount"]())._):
    m.post_applying = True

    @m.pull("lang.console", Nick)
    async def get_console_nick(self, target: Selector | None, r: type[Nick]) -> Nick:
        assert target is not None
        console = self.account.client.storage.current_user
        return Nick(console.nickname, console.nickname, "")

    @m.pull("lang.console", Summary)
    async def get_summary(self, target: Selector | None, r: type[Summary]) -> Summary:
        assert target is not None
        console = self.account.client.storage.current_user
        return Summary(
            console.nickname, console.nickname
        )
