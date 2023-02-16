import contextlib
from datetime import datetime
from typing import Any, Dict, TextIO, Optional, cast, TYPE_CHECKING
import sys
from textual.app import App, Reactive
from textual.widgets import Input
from textual.binding import Binding
from loguru import logger

from avilla.console.account import ConsoleAccount
from avilla.console.message import ConsoleMessage, Text
from .info import MessageEvent, Event
from .storage import Storage
from .router import RouterView
from .log_redirect import FakeIO
from .views.log_view import LogView
from .components.footer import Footer
from .components.header import Header
from .views.horizontal import HorizontalView

if TYPE_CHECKING:
    from avilla.console.protocol import ConsoleProtocol


class Frontend(App):
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+s", "screenshot", "Save a screenshot"),
        Binding("ctrl+underscore", "focus_input", "Focus input", key_display="ctrl+/"),
    ]

    ROUTES = {"main": lambda: HorizontalView(), "log": lambda: LogView()}

    def __init__(self, protocol: "ConsoleProtocol"):
        super().__init__()
        self.protocol = protocol
        self.title = "Avilla"#Reactive("Avilla")
        self.sub_title = "Welcome to console"#Reactive("Welcome to console")
        self.account = ConsoleAccount(protocol)
        self.storage = Storage()

        self._stderr = sys.stderr
        self._logger_id: Optional[int] = None
        self._should_restore_logger: bool = False
        self._fake_output = cast(TextIO, FakeIO(self.storage))
        self._redirect_stdout: Optional[contextlib.redirect_stdout[TextIO]] = None
        self._redirect_stderr: Optional[contextlib.redirect_stderr[TextIO]] = None


    def compose(self):
        yield Header()
        yield RouterView(self.ROUTES, "main")
        yield Footer()

    def on_load(self):
        logger.remove()
        self._should_restore_logger = True
        self._logger_id = logger.add(
            self._fake_output,
            level=0,
            diagnose=False
        )

    def on_mount(self):
        with contextlib.suppress(Exception):
            stdout = contextlib.redirect_stdout(self._fake_output)
            stdout.__enter__()
            self._redirect_stdout = stdout

        with contextlib.suppress(Exception):
            stderr = contextlib.redirect_stderr(self._fake_output)
            stderr.__enter__()
            self._redirect_stderr = stderr

    def on_unmount(self):
        if self._redirect_stderr is not None:
            self._redirect_stderr.__exit__(None, None, None)
            self._redirect_stderr = None
        if self._redirect_stdout is not None:
            self._redirect_stdout.__exit__(None, None, None)
            self._redirect_stdout = None

        if self._logger_id is not None:
            logger.remove(self._logger_id)
            self._logger_id = None
        if self._should_restore_logger:
            logger.add(
                self._stderr,
                backtrace=True,
                diagnose=True,
                colorize=True,
            )
            self._should_restore_logger = False
        logger.success("Console exit.")
        logger.warning("Press Ctrl-C for Application exit")

    async def call(self, api: str, data: Dict[str, Any]):
        if api == "send_msg":
            self.storage.write_chat(
                MessageEvent(
                    type="message",
                    time=datetime.now(),
                    self_id=data["info"].id,
                    message=data["message"],
                    user=data["info"],
                )
            )
        elif api == "bell":
            await self.action("bell")

    def action_focus_input(self):
        with contextlib.suppress(Exception):
            self.query_one(Input).focus()

    async def action_post_message(self, message: str):
        msg = MessageEvent(
            type="message",
            time=datetime.now(),
            self_id=self.account.id,
            message=ConsoleMessage([Text(message)]),
            user=self.storage.current_user
        )
        self.storage.write_chat(msg)
        event, context = await self.protocol.parse_event(self.account, msg, error=True)
        self.protocol.post_event(event, context)

    async def action_post_event(self, event: Event):
        avilla_event, context = await self.protocol.parse_event(self.account, event, error=True)
        self.protocol.post_event(avilla_event, context)

