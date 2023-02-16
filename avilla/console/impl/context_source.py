from __future__ import annotations
from typing import TYPE_CHECKING

from avilla.core.context import Context
from avilla.core.selector import Selector
from avilla.core.trait.context import ContextSourceRecorder

if TYPE_CHECKING:
    from ..account import ConsoleAccount

_source_record = ContextSourceRecorder["ConsoleAccount"]


@_source_record("friend")
async def get_console_context(account: ConsoleAccount, target: Selector, *, via: Selector | None = None) -> Context:
    console = target.land(account.land)
    return Context(account, account.to_selector(), console, console, account.to_selector(), [via] if via else [])
