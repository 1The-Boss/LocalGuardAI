print("REPORT MODEL LOADED")
import uuid
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID 
from app.db.database import Base
from sqlalchemy.sql import func

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    category = Column(String, nullable=True)    # AI-generated category
    priority_score = Column(Float, nullable=False, default=0.0)
    status = Column(String, default="open", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    image_path = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)


Index("idx_status", Report.status)
Index("idx_created", Report.created_at)
