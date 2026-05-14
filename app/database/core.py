from datetime import datetime
from fastapi import Depends
from typing import Annotated
from sqlalchemy import create_engine, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session, Mapped, mapped_column

from app.config import settings


engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]