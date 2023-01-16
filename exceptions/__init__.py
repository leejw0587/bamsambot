from discord.ext import commands


class UserBlacklisted(commands.CheckFailure):
    def __init__(self, message="User is blacklisted!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(commands.CheckFailure):
    def __init__(self, message="해당 유저는 관리자가 아닙니다!"):
        self.message = message
        super().__init__(self.message)


class UserNotInformant(commands.CheckFailure):
    def __init__(self, message="해당 유저는 권한을 가지고 있지 않습니다!"):
        self.message = message
        super().__init__(self.message)


class UserNotHasCheck(commands.CheckFailure):
    def __init__(self, message="해당 유저가 인증 역할을 보유하고 있지 않습니다!"):
        self.message = message
        super().__init__(self.message)
