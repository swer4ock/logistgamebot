# database.py

from sqlalchemy import create_engine, Column, String, BigInteger, ForeignKey, TIMESTAMP, DECIMAL, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://logistadmin:yourpassword@localhost/logistgame_db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(String, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_datetime = Column(TIMESTAMP, nullable=False)
    cargo_character = Column(String, nullable=False)
    cargo_tonnage = Column(DECIMAL, nullable=False)
    cargo_volume = Column(DECIMAL, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")

class Notification(Base):
    __tablename__ = 'notifications'
    
    notification_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String, ForeignKey('orders.order_id'))
    message = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, default=datetime.utcnow)

    order = relationship("Order")

# Создание таблиц
def init_db():
    Base.metadata.create_all(bind=engine)

