from aiopg.sa import create_engine
from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserGoogle(Base):
    __tablename__ = 'user_google'

    google_id = Column(String(50), primary_key=True)
    google_user = Column(String(50))
    google_email = Column(String(50))

    def __init__(self, google_id, google_user, google_email):
        self.google_id = google_id
        self.google_user = google_user
        self.google_email = google_email

    def __repr__(self):
        return '<UserGoogle: {} {}>'.format(self.google_id, self.google_user)


async def setup(app):
    connection_url = 'postgresql://{}:{}@{}/{}'.format(
        app.config.DATABASE['user'],
        app.config.DATABASE['password'],
        app.config.DATABASE['host'],
        app.config.DATABASE['database'])
    engine = await create_engine(connection_url)
    app.db = engine
    app.db.Base = Base


async def close(app):
    app.db.close()
    await app.db.wait_closed()
    app.db = None
