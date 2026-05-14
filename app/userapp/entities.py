from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.core import Base, TimestampMixin


class DocumentUser(TimestampMixin, Base):
    __tablename__ = 'document_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_pwd: Mapped[str] = mapped_column(String(250), nullable=False)

    documents = relationship('DocumentCollection', back_populates='owner')
    files = relationship('DocumentCollectionFile', back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"