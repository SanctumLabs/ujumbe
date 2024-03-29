"""
Logger configurations, this uses loguru to handle logs
Reference: https://github.com/Delgan/loguru
"""

import os
import sys

from loguru import logger as log

# configurations for log handling

# info log configurations
log.add(
    sink="logs/info.log" if os.environ.get("ENVIRONMENT") == "local" else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="INFO",
)

# error logs
log.add(
    sink="logs/error.log" if os.environ.get("ENVIRONMENT") == "local" else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="ERROR",
)

# debug logs
log.add(
    sink="logs/debug.log" if os.environ.get("ENVIRONMENT") == "local" else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="DEBUG",
)

# warning logs
log.add(
    sink="logs/warn.log" if os.environ.get("ENVIRONMENT") == "local" else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="WARNING",
)

# critical logs
log.add(
    sink="logs/critical.log"
    if os.environ.get("ENVIRONMENT") == "local"
    else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="CRITICAL",
)

# trace logs
log.add(
    sink="logs/trace.log" if os.environ.get("ENVIRONMENT") == "local" else sys.stdout,
    backtrace=True
    if os.environ.get("ENVIRONMENT", "development") == "development"
    else False,
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
    enqueue=True,
    level="TRACE",
)
