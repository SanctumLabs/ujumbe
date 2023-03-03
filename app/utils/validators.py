import phonenumbers


def is_valid_phone_number(phone_number: str) -> bool:
    number = phonenumbers.parse(phone_number, None)
    return phonenumbers.is_valid_number(number)
