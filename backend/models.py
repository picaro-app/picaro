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

    # Photographer khud decide karega event_id
    event_id = Column(String, primary_key=True, index=True)

    event_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    photographer_id = Column(Integer, ForeignKey("photographers.id"))
    photographer = relationship("Photographer", back_populates="events")