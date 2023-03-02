from app.core.domain.exceptions import AppException


class TaskException(AppException):
    def __init__(self, message=None):
        if message is None:
            self.message = "Worker failed to execute task"
