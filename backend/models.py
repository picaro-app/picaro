from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Photographer(Base):
    __tablename__ = "photographers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    events = relationship("Event", back_populates="photographer")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    event_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    photographer_id = Column(Integer, ForeignKey("photographers.id"))
    photographer = relationship("Photographer", back_populates="events")