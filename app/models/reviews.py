from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, DateTime
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String, nullable=True)
    comment_date = Column(DateTime, default=datetime.utcnow)
    grade = Column(Float)
    is_active = Column(Boolean, default=True)

    user = relationship('User', back_populates='reviews')
    product = relationship('Product', back_populates='reviews')
