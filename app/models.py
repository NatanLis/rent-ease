from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# --- USER ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    nickname = Column(String)

    # Relationships
    properties = relationship("Property", back_populates="owner", cascade="all, delete")
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender_user")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver_user")
    invoices = relationship("Invoice", back_populates="user")


# --- PROPERTY ---

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    address = Column(String)
    price = Column(Float)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="properties")


# --- ALERT ---

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    is_resolved = Column(Boolean, default=False)


# --- INVOICE ---

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String)
    is_paid = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="invoices")
    payment = relationship("Payment", back_populates="invoice", uselist=False)


# --- MESSAGE ---

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)

    sender_user = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver_user = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")


# --- PAYMENT ---

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    amount = Column(Float)
    status = Column(String)

    invoice = relationship("Invoice", back_populates="payment")
