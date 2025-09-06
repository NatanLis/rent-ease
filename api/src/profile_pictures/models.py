from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base


class ProfilePicture(Base):
    """Profile picture model for storing user profile images."""
    
    __tablename__ = "profile_pictures"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    user = relationship("User", back_populates="profile_picture")
