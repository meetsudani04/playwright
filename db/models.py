from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class SlackUser(Base):
    __tablename__ = 'slack_users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slack_id = Column(String, unique=True, index=True, nullable=False)
    hrms_username = Column(String, nullable=False)
    hrms_password = Column(String, unique=True, index=True, nullable=False)
    trigger_time = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)