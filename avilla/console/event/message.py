from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING


from graia.amnesia.message import __message_chain_class__
from graia.amnesia.builtins.memcache import Memcache
from avilla.core.context import Context
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import EventParserRecorder
from avilla.spec.core.message import MessageReceived
from ..frontend.info import MessageEvent

if TYPE_CHECKING:
    from ..account import ConsoleAccount
    from ..protocol import ConsoleProtocol

event = EventParserRecorder["ConsoleProtocol", "ConsoleAccount"]


@event("message")
async def console_message(
    protocol: ConsoleProtocol, account: ConsoleAccount, raw: MessageEvent
):
    console = Selector().land(protocol.land.name).console(str(raw.user.id))
    context = Context(
        account=account,
        client=console,
        endpoint=account.to_selector(),
        scene=console,
        selft=account.to_selector(),
    )
    message_result = await protocol.deserialize_message(context, raw.message)
    message = Message(
        describe=Message,
        id=str(raw.time.timestamp()),
        scene=console,
        sender=console,
        content=__message_chain_class__(message_result),
        time=datetime.fromtimestamp(raw.time.timestamp())
    )
    context._collect_metadatas(message, message)
    memcache = context.avilla.launch_manager.get_interface(Memcache)
    await memcache.set(f"_console_context.message.{message.id}", message, timedelta(seconds=300))
    res = MessageReceived(context, message)
    return res, context
