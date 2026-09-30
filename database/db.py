from sqlalchemy import create_engine,text
from config.settings import settings
engine = create_engine(settings.DATABASE_URL,echo=True)
print("connected")