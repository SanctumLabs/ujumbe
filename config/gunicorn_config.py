import multiprocessing
import os
from click import echo, style

if os.path.exists(".env"):
    echo(style(text="Importing environment variables", fg="green", bold=True))
    for line in open(".env"):
        var = line.strip().split("=")
        if len(var) == 2:
            os.environ[var[0]] = var[1]

bind = f"0.0.0.0:{os.environ.get('PORT', 4000)}"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "-"  # STDOUT
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "debug" if os.environ.get("FLASK_ENV") == "development" else "info"
capture_output = True
enable_stdio_inheritance = True