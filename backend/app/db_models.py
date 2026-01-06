"""
数据库模型定义
包含用户表和旅行计划表
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联历史记录
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")


class Itinerary(Base):
    """旅行计划表"""
    __tablename__ = "itineraries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 请求信息
    agent_name = Column(String(255))
    destination = Column(String(255), nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(String(100))
    travelers = Column(Integer)
    preferences = Column(Text)  # JSON 字符串
    extra_requirements = Column(Text)
    
    # 生成的行程（JSON 格式）
    itinerary_data = Column(Text, nullable=False)  # 完整的 JSON 数据
    
    # 快速检索字段
    total_budget = Column(Float)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联用户
    user = relationship("User", back_populates="itineraries")
