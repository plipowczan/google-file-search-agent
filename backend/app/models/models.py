from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


class Store(Base):
    """Store model representing a FileSearchStore in Google Cloud"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, unique=True, nullable=False, index=True)  # User-facing name
    google_store_name = Column(String, unique=True, nullable=False, index=True)  # Google FileSearchStore name (e.g., "fileSearchStores/abc-123")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to files
    files = relationship("File", back_populates="store", cascade="all, delete-orphan")


class File(Base):
    """File model representing documents in a FileSearchStore"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String, nullable=False)  # Document ID in FileSearchStore
    display_name = Column(String, nullable=False)  # User-facing filename
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="IMPORTING")  # IMPORTING, COMPLETED, FAILED
    
    # Relationship to store
    store = relationship("Store", back_populates="files")
