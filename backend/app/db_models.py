"""
数据库模型定义
包含用户表和旅行计划表
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, UniqueConstraint
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


class EmailVerification(Base):
    """邮箱验证码表"""
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    verification_code = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ShareLink(Base):
    """分享链接表"""
    __tablename__ = "share_links"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    is_public = Column(Integer, default=1, nullable=False)  # 1=公开, 0=私密
    expires_at = Column(DateTime(timezone=True), nullable=True)  # None表示永久有效
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联行程
    itinerary = relationship("Itinerary", foreign_keys=[itinerary_id])


class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 唯一约束：一个用户不能重复收藏同一个行程
    __table_args__ = (
        UniqueConstraint('user_id', 'itinerary_id', name='uq_user_itinerary'),
    )


class TemporaryShare(Base):
    """临时分享表（用于游客用户分享）"""
    __tablename__ = "temporary_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    itinerary_data = Column(Text, nullable=False)  # 完整的行程数据（JSON格式）
    expires_at = Column(DateTime(timezone=True), nullable=False)  # 必须设置过期时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
