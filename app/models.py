from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    target_url = Column(String, nullable=False)
    short_key = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    visits = Column(Integer, default=0)