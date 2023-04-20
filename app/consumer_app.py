"""
Consumer Application Entry point
"""
from fastapi import FastAPI
from app.config.di.container import ApplicationContainer
from app.infra.handlers.exception_handlers import attach_exception_handlers
from app.settings import config

container = ApplicationContainer()

consumer_app = FastAPI(
    title=f"{config.server_name} Consumer",
    description='Ujumbe consumer application',
    version="1.0.0"
)

consumer_app.container = container
attach_exception_handlers(app=consumer_app)
