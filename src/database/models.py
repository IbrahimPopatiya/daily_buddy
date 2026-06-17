from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

def _uuid_str():
    return str(uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=_uuid_str)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    content_type = Column(String(50), index=True)
    extracted_data = Column(Text)  # JSON stored as text
    embedding_vector = Column(Text)
    tags = Column(Text)  # JSON array stored as text
    category = Column(String(100))
    extraction_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"))
    operation = Column(String(50))
    resource_type = Column(String(100))
    resource_id = Column(String(36))
    new_value = Column(Text)  # JSON stored as text
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
