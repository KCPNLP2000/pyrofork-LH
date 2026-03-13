from typing import Union, Optional
from enum import Enum

import pyrogram
from pyrogram import raw
from pyrogram import types
from ..object import Object


class KeyboardButtonStyle(Enum):
    """Telegram Bot API 9.4+ button styles."""
    DEFAULT = "default"
    PRIMARY = "primary"  # Blue
    SUCCESS = "success"  # Green  
    DANGER = "danger"    # Red


class InlineKeyboardButton(Object):
    """One button of an inline keyboard.

    You must use exactly one of the optional fields.

    Parameters:
        text (``str``):
            Label text on the button.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the Web App that will be launched when the user presses the button.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
            An HTTP URL used to automatically authorize the user.

        user_id (``int``, *optional*):
            User id, for links to the user profile.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username in the current chat's input field.

        callback_game (:obj:`~pyrogram.types.CallbackGame`, *optional*):
            Description of the game that will be launched when the user presses the button.

        pay (``bool``, *optional*):
            Payment button.

        requires_password (``bool``, *optional*):
            Requires 2FA password for callback data.

        copy_text (``str``, *optional*):
            Text to copy to clipboard.

        icon_custom_emoji_id (``str``, *optional*):
            Custom emoji identifier for the button icon (Bot API 9.4+).

        icon_url (``str``, *optional*):
            URL of PNG icon (max 1MB, Bot API 9.4+).

        style (:obj:`~pyrogram.types.KeyboardButtonStyle`, *optional*):
            Button color style (Bot API 9.4+): default, primary (blue), success (green), danger (red).
    """

    def __init__(
        self,
        text: str,
        callback_data: Optional[Union[str, bytes]] = None,
        url: Optional[str] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        user_id: Optional[int] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        callback_game: Optional["types.CallbackGame"] = None,
        pay: Optional[bool] = None,
        requires_password: Optional[bool] = None,
        copy_text: Optional[str] = None,
        icon_custom_emoji_id: Optional[str] = None,
        icon_url: Optional[str] = None,
        style: Optional[KeyboardButtonStyle] = None
    ):
        super().__init__()

        self.text = str(text)
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.login_url = login_url
        self.user_id = user_id
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game
        self.pay = pay
        self.requires_password = requires_password
        self.copy_text = copy_text
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.icon_url = icon_url
        self.style = style.value if style else None

    @staticmethod
    def read(b: "raw.base.KeyboardButton"):
        style = getattr(b, "style", None)
        
        if isinstance(b, raw.types.KeyboardButtonCallback):
            try:
                data = b.data.decode()
            except UnicodeDecodeError:
                data = b.data

            return InlineKeyboardButton(
                text=b.text,
                callback_data=data,
                requires_password=getattr(b, "requires_password", None),
                icon_custom_emoji_id=getattr(b, "icon_custom_emoji_id", None),
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonUrl):
            return InlineKeyboardButton(
                text=b.text,
                url=b.url,
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonUrlAuth):
            return InlineKeyboardButton(
                text=b.text,
                login_url=types.LoginUrl.read(b),
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonUserProfile):
            return InlineKeyboardButton(
                text=b.text,
                user_id=b.user_id,
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonSwitchInline):
            if b.same_peer:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_current_chat=b.query,
                    style=style
                )
            else:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query=b.query,
                    style=style
                )

        if isinstance(b, raw.types.KeyboardButtonGame):
            return InlineKeyboardButton(
                text=b.text,
                callback_game=types.CallbackGame(),
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonWebView):
            return InlineKeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(url=b.url),
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonCopy):
            return InlineKeyboardButton(
                text=b.text,
                copy_text=b.copy_text,
                style=style
            )

        if isinstance(b, raw.types.KeyboardButtonBuy):
            return InlineKeyboardButton(
                text=b.text,
                pay=True,
                style=style
            )

    async def write(self, client: "pyrogram.Client"):
        # Helper to create styled buttons
        def create_styled_button(base_type, **kwargs):
            btn = base_type(**kwargs)
            if self.style:
                if not hasattr(btn, 'style'):
                    # Add style attribute dynamically if supported by MTProto
                    btn.style = self.style
                if self.icon_custom_emoji_id:
                    btn.icon_custom_emoji_id = self.icon_custom_emoji_id
            return btn

        if self.callback_data is not None:
            data = bytes(self.callback_data, "utf-8") if isinstance(self.callback_data, str) else self.callback_data
            return create_styled_button(
                raw.types.KeyboardButtonCallback,
                text=self.text,
                data=data,
                requires_password=self.requires_password
            )

        if self.pay:
            return create_styled_button(
                raw.types.KeyboardButtonBuy,
                text=self.text
            )

        if self.url is not None:
            return create_styled_button(
                raw.types.KeyboardButtonUrl,
                text=self.text,
                url=self.url
            )

        if self.icon_url is not None:
            # icon_url maps to web_app-like behavior or URL button with styling
            return create_styled_button(
                raw.types.KeyboardButtonUrl,
                text=self.text,
                url=self.icon_url
            )

        if self.login_url is not None:
            btn = self.login_url.write(
                text=self.text,
                bot=await client.resolve_peer(self.login_url.bot_username or "self")
            )
            if self.style:
                btn.style = self.style
            return btn

        if self.user_id is not None:
            btn = raw.types.InputKeyboardButtonUserProfile(
                text=self.text,
                user_id=await client.resolve_peer(self.user_id)
            )
            if self.style:
                btn.style = self.style
            return btn

        if self.switch_inline_query is not None:
            return create_styled_button(
                raw.types.KeyboardButtonSwitchInline,
                text=self.text,
                query=self.switch_inline_query
            )

        if self.switch_inline_query_current_chat is not None:
            return create_styled_button(
                raw.types.KeyboardButtonSwitchInline,
                text=self.text,
                query=self.switch_inline_query_current_chat,
                same_peer=True
            )

        if self.callback_game is not None:
            return create_styled_button(
                raw.types.KeyboardButtonGame,
                text=self.text
            )

        if self.web_app is not None:
            return create_styled_button(
                raw.types.KeyboardButtonWebView,
                text=self.text,
                url=self.web_app.url
            )

        if self.copy_text is not None:
            return create_styled_button(
                raw.types.KeyboardButtonCopy,
                text=self.text,
                copy_text=self.copy_text
            )

        raise ValueError("InlineKeyboardButton requires exactly one of the optional fields")
