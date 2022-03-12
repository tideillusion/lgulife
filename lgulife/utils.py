class MyException(Exception):
    def __init__(self, msg=None):
        super().__init__(self)
        self.msg = msg

    def __str__(self):
        pass


class NotFoundError(MyException):
    def __str__(self):
        return f"Request source {self.msg} not found on server."


class ReadOnlyError(MyException):
    def __str__(self):
        return f"{self.msg} is read-only."


class InvalidVersionError(MyException):
    def __str__(self):
        return f"Input version ({self.msg}) not exists. Recheck input or update meta."


class CommentAlreadyDeletedError(MyException):
    def __str__(self):
        return f"This Comment has been already deleted after {self.msg}."


class CommentNotCreatedError(MyException):
    def __str__(self):
        return f"This Comment has not been created until {self.msg}."
