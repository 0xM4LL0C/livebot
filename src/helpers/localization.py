from typing import Any

from i18n import I18N

from data.items.utils import get_item_emoji
from helpers.utils import pretty_float, pretty_int

i18n = I18N("ru", "src/locales")


i18n.register_function("int", int)
i18n.register_function("get_item_emoji", get_item_emoji)
i18n.register_function("pretty_float", pretty_float)
i18n.register_function("pretty_int", pretty_int)
i18n.register_function("t", i18n.t)

i18n.register_constant("CHANNEL_USERNAME", "@LiveBotOfficial")
i18n.register_constant("CHAT_USERNAME", "@LiveBotOfficialChat")
i18n.register_constant("GUIDE_URL", "https://0xM4LL0C.github.io/livebot/guide")


def t(locale: str, key: str, **kwargs: Any):
    i18n.load()
    return i18n.t(locale, key, **kwargs)
