from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from database.models import UserModel, UserViolation
from helpers.datetime_utils import utcnow
from helpers.localization import t
from helpers.utils import parse_time_duration


router = Router()


@router.message(Command("warn"))
async def warn_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    reason = command.args

    if not reason:
        return

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)
    reply_user.violations.append(UserViolation(reason=reason, type="warn"))

    await reply_user.update_async()

    await message.reply(t("warn", user=reply_user, reason=reason))


@router.message(Command("mute"))
async def mute_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    args = command.args
    if args is None:
        return
    args = args.strip().split(" ")
    time_str = args[0]
    reason = " ".join(args[1:]) if len(args) > 1 else "Без причины"

    try:
        until_date = utcnow() + parse_time_duration(time_str)
    except ValueError as e:
        await message.reply(str(e))
        return

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)
    reply_user.violations.append(
        UserViolation(
            reason=reason,
            type="mute",
            until_date=until_date,
        )
    )

    await reply_user.update_async()

    await message.chat.restrict(
        reply_user.id,
        permissions=ChatPermissions(can_send_message=False),
        until_date=until_date,
    )

    await message.reply(t("mute", user=reply_user, reason=reason, until_date=until_date))


@router.message(Command("ban"))
async def ban_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    args = command.args
    if args is None:
        return
    args = args.strip().split(" ")
    time_str = args[0]
    reason = " ".join(args[1:]) if len(args) > 1 else "Без причины"

    try:
        until_date = utcnow() + parse_time_duration(time_str)
    except ValueError as e:
        await message.reply(str(e))
        return

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)
    reply_user.violations.append(
        UserViolation(
            reason=reason,
            type="ban",
            until_date=until_date,
        )
    )

    await reply_user.update_async()

    await message.chat.ban(
        reply_user.id,
        until_date=until_date,
    )

    await message.reply(t("ban", user=reply_user, reason=reason, until_date=until_date))


@router.message(Command("pban"))
async def pban_cmd(message: Message, command: CommandObject):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    reason = command.args or "Без причины"

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)
    reply_user.violations.append(
        UserViolation(
            reason=reason,
            type="permanent-ban",
        )
    )

    await reply_user.update_async()

    await message.chat.ban(
        reply_user.id,
    )

    await message.reply(t("permanent-ban", user=reply_user, reason=reason))


@router.message(Command("unmute"))
async def unmute_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)

    await message.chat.restrict(
        reply_user.id,
        permissions=ChatPermissions(can_send_messages=True),
    )

    reply_user.violations = [
        violation for violation in reply_user.violations if violation.type not in ["mute"]
    ]

    await reply_user.update_async()

    await message.reply(t("unmute", user=reply_user))


@router.message(Command("unban"))
async def unban_cmd(message: Message):
    user = await UserModel.get_async(id=message.from_user.id)

    if not user.is_admin:
        return

    if not message.reply_to_message:
        return

    reply_user = await UserModel.get_async(id=message.reply_to_message.from_user.id)

    reply_user.violations = [
        violation
        for violation in reply_user.violations
        if violation.type not in ["ban", "permanent-ban"]
    ]
    await reply_user.update_async()
    await message.chat.unban(reply_user.id)

    await message.reply(t("unban", user=reply_user))
