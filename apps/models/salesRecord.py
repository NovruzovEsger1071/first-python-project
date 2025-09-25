from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from apps.core.database import Base

class SalesRecord(Base):
    __tablename__ = 'sales_records'
    id = Column(Integer, primary_key=True)
    uploaded_file_id = Column(String, ForeignKey('uploaded_files.id'))
    date = Column(String)
    product_name = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    region = Column(String)

    uploaded_file = relationship("UploadedFile", back_populates="sales_records")