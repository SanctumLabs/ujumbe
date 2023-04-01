"""
Application exceptions
"""


class AppException(Exception):
    """Base Exception for errors raised by application"""


class DomainException(Exception):
    """Base Exception for errors raised by a domain"""


class BusinessRuleValidationException(DomainException):
    def __init__(self, rule):
        self.rule = rule

    def __str__(self):
        return str(self.rule)


class EntityNotFoundException(Exception):
    entity_name: str

    def __init__(self, entity_id):
        message = f"{self.entity_name} {entity_id} not found"
        super().__init__(message)
        self.entity_id = entity_id
