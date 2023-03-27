from .mixins import BusinessRuleValidationMixin


class Service(BusinessRuleValidationMixin):
    """
    Services carry domain knowledge that does not fit naturally in entities and value objects
    """
