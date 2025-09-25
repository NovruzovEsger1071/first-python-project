from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from apps.core.database import Base

class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"
    id = Column(Integer, primary_key=True, index=True)
    uploaded_file_id = Column(String, ForeignKey("uploaded_files.id"), unique=True)
    total_sales_product = Column(JSON)
    total_sales_region = Column(JSON)
    monthly_trends = Column(JSON)

    uploaded_file = relationship("UploadedFile", back_populates="analytics_summary")