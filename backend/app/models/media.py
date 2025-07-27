from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class MediaAnalysis(Base):
    __tablename__ = "media_analysis"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    media_type = Column(String, index=True)  # 'image' or 'video'
    summary = Column(Text)
    transcript = Column(Text)
    media_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
