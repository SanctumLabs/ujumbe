import uvicorn
import os

host = os.environ.get("HOST", "0.0.0.0")
port = os.environ.get("PORT", 5000)
reload = os.environ.get("ENV", "development") == "development"

if __name__ == "__main__":
    uvicorn.run("app:app", host=host, port=port, reload=reload)
