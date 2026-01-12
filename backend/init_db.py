"""
数据库初始化脚本
运行此脚本创建所有表
"""
import sys
import io

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import engine, Base
from app.db_models import User, Itinerary, EmailVerification, ShareLink, Favorite, TemporaryShare

def init_db():
    """初始化数据库，创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建成功！")
    print(f"[OK] 创建的表: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_db()
