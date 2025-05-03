from typing import Any

from i18n import I18N

from consts import VERSION
from data.items.utils import get_item_emoji
from helpers.datetime_utils import utcnow
from helpers.utils import get_time_difference_string, pretty_datetime, pretty_float, pretty_int


i18n = I18N("ru", "src/locales")


i18n.register_function("int", int)
i18n.register_function("get_item_emoji", get_item_emoji)
i18n.register_function("pretty_float", pretty_float)
i18n.register_function("pretty_int", pretty_int)
i18n.register_function("pretty_datetime", pretty_datetime)
i18n.register_function("utcnow", utcnow)
i18n.register_function("get_time_difference_string", get_time_difference_string)

i18n.register_constant("CHANNEL_USERNAME", "@LiveBotOfficial")
i18n.register_constant("CHAT_USERNAME", "@LiveBotOfficialChat")
i18n.register_constant("GUIDE_URL", "https://0xM4LL0C.github.io/livebot/guide")
i18n.register_constant("VERSION", str(VERSION))


def t(key: str, **kwargs: Any) -> str:
    i18n.load()
    return i18n.t(i18n.default_locale, key, **kwargs)


i18n.register_function("t", t)
