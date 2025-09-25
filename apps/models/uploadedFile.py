from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from apps.core.database import Base
from datetime import datetime

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="uploaded_files")
    sales_records = relationship("SalesRecord", back_populates="uploaded_file")
    analytics_summary = relationship("AnalyticsSummary", back_populates="uploaded_file", uselist=False)