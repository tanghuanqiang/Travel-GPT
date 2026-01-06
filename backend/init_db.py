"""
数据库初始化脚本
运行此脚本创建所有表
"""
from app.database import engine, Base
from app.db_models import User, Itinerary

def init_db():
    """初始化数据库，创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")
    print(f"✅ 创建的表: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_db()
