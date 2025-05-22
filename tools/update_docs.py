import shutil
import sys
from contextlib import suppress
from pathlib import Path


sys.path.insert(0, "src/")

from livebot.data.achievements.achievements import ACHIEVEMENTS
from livebot.data.items.items import ITEMS
from livebot.data.items.utils import get_item_emoji


DOCS_PATH = Path("docs/")

with suppress(shutil.SameFileError):
    shutil.copy("README.md", DOCS_PATH / "index.md")

with suppress(shutil.SameFileError):
    shutil.copy("CHANGELOG.md", DOCS_PATH / "changelog.md")


items_text = "# Информация о предметах\n\n"

for item in ITEMS:
    items_text += f"## {item.emoji} {item.name}\n\n"
    items_text += f"**Редкость:** _{item.rarity.value}_\n\n"
    items_text += f"**Описание:** _{item.desc}_\n\n"

    if item.craft:
        items_text += "**Крафт:** "
        items_text += ", ".join(
            [
                f"[{get_item_emoji(craft.name)} {craft.name} {craft.quantity}](#{craft.name})"
                for craft in item.craft
            ]
        )

        items_text += "\n\n"

with open(DOCS_PATH / "items.md", "w") as f:
    f.seek(0)
    f.write(items_text)

achievements_text = "# Информация об достижениях\n\n"

for achievement in ACHIEVEMENTS:
    achievements_text += f"## {achievement.emoji} {achievement.name}\n\n"
    achievements_text += f"**Описание:** _{achievement.desc}_\n\n"
    achievements_text += "**Награда:** "

    achievements_text += ", ".join(
        [
            f"[{get_item_emoji(item.name)} {item.name} {item.quantity}](items.md#{item.name})"
            for item in achievement.reward
        ]
    )

    achievements_text += "\n\n"

with open(DOCS_PATH / "items.md", "w") as f:
    f.seek(0)
    f.write(items_text)

with open(DOCS_PATH / "achievements.md", "w") as f:
    f.seek(0)
    f.write(achievements_text)
