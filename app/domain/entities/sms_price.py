"""
SmsPrice value object represents an SMS Price in the system
"""
from typing import Optional, Union
from dataclasses import dataclass
from app.core.domain.entities.value_object import ValueObject


@dataclass
class SmsPrice(ValueObject):
    price: Optional[Union[str, float]] = None
    currency: Optional[str] = None

    def __post_init__(self):
        amount = self.price
        if amount:
            if isinstance(amount, str):
                if not amount.replace(".", "", 1).isdigit():
                    raise ValueError(f"Price {amount} is not valid")
            if isinstance(amount, float):
                if amount < 0:
                    raise ValueError(f"Price {amount} is less than 0")

    def __repr__(self):
        return f"{self.currency} {self.price}"

    @property
    def amount(self) -> Optional[float]:
        """
        Amount Property to retrieve the amount(price) as a float

        Returns: None if the price is not defined or a float representation of the price

        Raises: ValueError is raised if the price cannot be parsed to a float
        """
        try:
            return None if not self.price else float(self.price)
        except ValueError as e:
            raise e

    def __str__(self) -> str:
        """
        Displays the sms price with the currency & the price in the format CURRENCY CODE PRICE, e.g. EUR 1.2
        Returns: full display of the price
        """
        return f"{self.currency} {self.price}"
