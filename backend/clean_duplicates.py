"""清理重复的历史记录"""
import sys
sys.path.insert(0, 'D:\\gitRepositories\\Travel-GPT\\backend')

from app.database import SessionLocal
from app.db_models import Itinerary
from sqlalchemy import func
from datetime import datetime

def clean_duplicate_records():
    db = SessionLocal()
    try:
        # 获取所有用户
        user_ids = db.query(Itinerary.user_id).distinct().all()
        
        total_deleted = 0
        
        for (user_id,) in user_ids:
            print(f"\n检查用户 {user_id} 的记录...")
            
            # 获取该用户的所有记录，按时间排序
            records = db.query(Itinerary)\
                .filter(Itinerary.user_id == user_id)\
                .order_by(Itinerary.created_at.desc())\
                .all()
            
            # 按 destination + days 分组
            groups = {}
            for record in records:
                key = f"{record.destination}_{record.days}"
                if key not in groups:
                    groups[key] = []
                groups[key].append(record)
            
            # 找出重复的记录
            for key, group in groups.items():
                if len(group) > 1:
                    print(f"  发现重复: {key} - {len(group)} 条记录")
                    
                    # 保留最新的一条，删除其他
                    to_keep = group[0]  # 已按时间降序排序，第一个是最新的
                    to_delete = group[1:]
                    
                    print(f"    保留: ID={to_keep.id}, 创建于 {to_keep.created_at}")
                    
                    for record in to_delete:
                        print(f"    删除: ID={record.id}, 创建于 {record.created_at}")
                        db.delete(record)
                        total_deleted += 1
        
        # 提交删除
        if total_deleted > 0:
            confirm = input(f"\n总共将删除 {total_deleted} 条重复记录，确认？(yes/no): ")
            if confirm.lower() == 'yes':
                db.commit()
                print(f"\n✓ 成功删除 {total_deleted} 条重复记录")
            else:
                db.rollback()
                print("\n✗ 已取消删除")
        else:
            print("\n✓ 没有发现重复记录")
    
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("清理重复历史记录")
    print("=" * 60)
    clean_duplicate_records()
