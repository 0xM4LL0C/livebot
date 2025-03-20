class BotException(Exception):
    pass


class NoResult(BotException):
    pass


class AlreadyExists(BotException):
    pass


class UserNotFoundError(BotException):
    pass


class ItemIsCoin(BotException):
    pass


class QuestNotFound(BotException):
    pass


class AchievementNotFoundError(BotException):
    pass


class ItemNotFoundError(BotException):
    pass
