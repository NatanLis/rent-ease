from sqlalchemy import Column, DateTime, Integer, LargeBinary, String, func

from api.core.database import Base


class File(Base):
    """File model for storing uploaded files."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
