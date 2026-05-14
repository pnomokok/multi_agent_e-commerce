from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String
from app.database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String, nullable=False)  # orchestrator/negotiator/logistics/data
    action = Column(String, nullable=False)
    payload = Column(JSON, default=dict)
