from sqlalchemy import create_engine


class DatabaseClient:
    def __init__(self, db_url: str):
        self.engine = create_engine(url=db_url)
