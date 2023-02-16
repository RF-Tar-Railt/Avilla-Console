from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger
from typing import TYPE_CHECKING
from graia.amnesia.builtins.memcache import Memcache
from avilla.console.account import ConsoleAccount


from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.core.trait.context import bounds, implement, pull
from avilla.spec.core.message import MessageSend
from avilla.spec.core.profile.metadata import Nick, Summary

from ..frontend.info import Robot
from ..message import ConsoleMessage

if TYPE_CHECKING:
    from graia.amnesia.message import __message_chain_class__

    from avilla.core.context import Context
    from ..protocol import ConsoleProtocol


with bounds("console"):

    @implement(MessageSend.send)
    async def send_console_message(
        ctx: Context, target: Selector, message: __message_chain_class__, *, reply: Selector | None = None
    ) -> Selector:
        if TYPE_CHECKING:
            assert isinstance(ctx.protocol, ConsoleProtocol)
        serialized_msg = await ctx.protocol.serialize_message(message, ctx)

        await ctx.account.call(
            "send_msg",
            {
                "message": ConsoleMessage(serialized_msg),
                "info": Robot("console")
            }
        )
        logger.info(  # TODO: wait for solution of ActiveMessage
            f"{ctx.account.land.name}: [send]"
            f"[Console]"
            f" <- {str(message)!r}"
        )
        message_metadata = Message(
            describe=Message,
            id=str(datetime.now().timestamp()),
            scene=Selector().land(ctx.land).console(str(target.pattern["console"])),
            content=message,
            time=datetime.now(),
            sender=ctx.account.to_selector(),
        )
        message_selector = message_metadata.to_selector()
        ctx._collect_metadatas(message_selector, message_metadata)
        memcache = ctx.avilla.launch_manager.get_interface(Memcache)
        await memcache.set(f"_console_context.message.{message_metadata.id}", message, timedelta(seconds=300))
        return message_selector


    @pull(Nick)
    async def get_console_nick(ctx: Context, target: Selector | None) -> Nick:
        assert target is not None
        assert isinstance(ctx.account, ConsoleAccount)
        console = ctx.account.client.storage.current_user
        return Nick(Nick, console.nickname, console.nickname, "")

    @pull(Summary)
    async def get_summary(ctx: Context, target: Selector | None) -> Summary:
        assert target is not None
        assert isinstance(ctx.account, ConsoleAccount)
        console = ctx.account.client.storage.current_user
        return Summary(
            describe=Summary, name=console.nickname, description=console.nickname
        )
