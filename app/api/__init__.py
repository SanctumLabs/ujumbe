# flake8: noqa
from flask import Blueprint

sms = Blueprint(
    name="SmsApi",
    import_name=__name__,
    url_prefix=f"/api/v1/sms",
    static_folder="static",
    template_folder="templates",
)

from .routers import sms
