from typing import Union, Optional, Iterator
from dataclasses import dataclass, field, asdict

from graia.amnesia.message import MessageChain as BaseMessageChain
from graia.amnesia import message
from graia.amnesia.message.element import Element, Text as BaseText
from rich.console import Console, ConsoleOptions, JustifyMethod, RenderResult
from rich.emoji import Emoji as RichEmoji
from rich.emoji import EmojiVariant
from rich.markdown import Markdown as RichMarkdown
from rich.measure import Measurement, measure_renderables
from rich.segment import Segment
from rich.style import Style
from rich.text import Text as RichText


class Text(BaseText):

    @property
    def rich(self) -> RichText:
        return RichText(self.text, end="")

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class Emoji(Element):
    name: str

    def __init__(self, name: str):
        self.name = name

    @property
    def rich(self) -> RichEmoji:
        return RichEmoji(self.name)

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


@dataclass
class Markup(Element):
    markup: str
    style: Union[str, Style] = field(default="none")
    emoji: bool = field(default=True)
    emoji_variant: Optional[EmojiVariant] = field(default=None)

    @property
    def rich(self) -> RichText:
        return RichText.from_markup(
            self.markup,
            style=self.style,
            emoji=self.emoji,
            emoji_variant=self.emoji_variant,
            end="",
        )

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


@dataclass
class Markdown(Element):
    markup: str
    code_theme: str = field(default="monokai")
    justify: Optional[JustifyMethod] = field(default=None)
    style: Union[str, Style] = field(default="none")
    hyperlinks: bool = field(default=True)
    inline_code_lexer: Optional[str] = field(default=None)
    inline_code_theme: Optional[str] = field(default=None)

    @property
    def rich(self) -> RichMarkdown:
        return RichMarkdown(**asdict(self))

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class ConsoleMessage(BaseMessageChain):

    def __init__(self, elements: list[Element]):
        """从传入的序列(可以是元组 tuple, 也可以是列表 list) 创建消息链.
        Args:
            elements (list[T]): 包含且仅包含消息元素的序列
        Returns:
            MessageChain: 以传入的序列作为所承载消息的消息链
        """
        super().__init__(elements)
        if not self.only(Text, Emoji, Markup, Markdown):
            raise ValueError(self)

    def __iter__(self) -> Iterator[Union[Text, Emoji, Markup, Markdown]]:
        yield from self.content

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from self
        if self.content and not isinstance(self.content[-1], Markdown):
            yield Segment("\n")

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, self)


# message.__message_chain_class__ = MessageChain
# message.__text_element_class__ = Text
ConsoleElement = Union[Text, Emoji, Markup, Markdown]
