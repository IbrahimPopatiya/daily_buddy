from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    content_type = Column(String(50), index=True)
    extracted_data = Column(JSONB)
    embedding_vector = Column(String)  # Stored as string or vector depending on PG extensions
    tags = Column(ARRAY(String))
    category = Column(String(100))
    extraction_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    operation = Column(String(50))
    resource_type = Column(String(100))
    resource_id = Column(UUID)
    new_value = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
