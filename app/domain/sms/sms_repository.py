"""
Sms Repository handling CRUD operations on an SMS & SMS Response
"""
from abc import ABCMeta
from app.core.domain.repository import Repository


class SmsRepository(Repository, metaclass=ABCMeta):
    """Sms Repository"""
