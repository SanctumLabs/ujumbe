from app.exceptions import SmsGatewayError


class TaskException(SmsGatewayError):
    def __init__(self, message=None):
        if message is None:
            self.message = "Worker failed to execute task"
