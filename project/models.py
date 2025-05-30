from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

class Number(BaseModel):
    number: int

from database import Base, engine

class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False) 
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now()) 
    price = Column(Float, nullable=False) 

    def __repr__(self):
        return f"<StockPriceHistory(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"


class UserEstimation(Base):
    __tablename__ = "user_estimations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    purchase_id = Column(String, unique=True, index=True, nullable=False) 
    total_estimated_gain = Column(Float, nullable=False) 
    detailed_estimations_json = Column(JSON, nullable=False) 
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now()) 

    def __repr__(self):
        return f"<UserEstimation(user_id='{self.user_id}', purchase_id='{self.purchase_id}', total_gain={self.total_estimated_gain})>"


def create_db_tables():
    Base.metadata.create_all(bind=engine)