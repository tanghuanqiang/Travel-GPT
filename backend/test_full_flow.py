"""测试完整的行程生成和图片添加流程"""
import asyncio
import os
import logging
from dotenv import load_dotenv

# 配置日志 - 显示所有级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

from app.models import TravelRequest, Activity, DailyPlan, TravelItinerary, BudgetOverview, HiddenGem, PracticalTips
from app.image_search import get_image_for_activity

def test_add_images():
    """测试图片添加逻辑"""
    print("\n" + "="*80)
    print("🧪 测试图片添加逻辑")
    print("="*80)
    
    # 创建模拟的行程数据（模拟 LLM 生成了 picsum 图片）
    mock_activities = [
        Activity(
            time="09:00",
            title="外滩",
            description="免费活动。中国最著名的地标之一...",
            duration="1.5小时",
            cost=0.0,
            address="黄浦区中山东一路",
            reason="上海地标，必游景点",
            images=["https://picsum.photos/800/600?random=1", "https://picsum.photos/800/600?random=2"]  # 模拟 LLM 生成的占位图
        ),
        Activity(
            time="11:00",
            title="南京路步行街",
            description="购物体验...",
            duration="2小时",
            cost=0.0,
            address="黄浦区南京东路",
            reason="购物天堂",
            images=["https://picsum.photos/800/600?random=3"]  # 模拟 LLM 生成的占位图
        )
    ]
    
    mock_daily_plan = DailyPlan(
        day=1,
        title="Day 1: 上海经典一日游",
        activities=mock_activities
    )
    
    mock_itinerary = TravelItinerary(
        overview=BudgetOverview(totalBudget=3000.0, budgetBreakdown=[]),
        dailyPlans=[mock_daily_plan],
        hiddenGems=[],
        practicalTips=PracticalTips(
            transportation="地铁出行",
            packingList=["舒适鞋子"],
            weather="晴朗",
            seasonalNotes="注意防晒"
        )
    )
    
    print("\n📋 模拟数据创建完成")
    print(f"   活动数量: {len(mock_activities)}")
    
    # 检查初始状态
    print("\n🔍 初始状态（模拟 LLM 生成的 picsum 图片）:")
    for activity in mock_activities:
        print(f"   - {activity.title}: {activity.images}")
    
    # 测试清除逻辑
    print("\n🧹 测试图片清除逻辑...")
    cleaned_count = 0
    for daily_plan in mock_itinerary.dailyPlans:
        for activity in daily_plan.activities:
            if hasattr(activity, 'images') and activity.images:
                old_images = activity.images.copy()
                activity.images = []
                cleaned_count += 1
                print(f"   ⚠️  清除了 '{activity.title}' 的 {len(old_images)} 张图片")
                for img in old_images[:1]:
                    if 'picsum' in img or 'placeholder' in img or 'placehold' in img:
                        print(f"      ❌ 占位图: {img}")
    
    print(f"\n✅ 已清除 {cleaned_count} 个活动的原有图片")
    
    # 测试图片获取
    print("\n📸 测试从 API 获取图片...")
    destination = "上海"
    
    for daily_plan in mock_itinerary.dailyPlans:
        print(f"\n📅 Day {daily_plan.day}: {daily_plan.title}")
        print("-" * 60)
        
        for idx, activity in enumerate(daily_plan.activities, 1):
            print(f"\n🎯 处理活动 {idx}: {activity.title}")
            
            # 确定活动类型
            category = ""
            if "餐" in activity.title or "吃" in activity.title or "美食" in activity.title:
                category = "美食"
            elif "博物" in activity.title or "寺" in activity.title or "庙" in activity.title:
                category = "博物馆"
            elif "公园" in activity.title or "花园" in activity.title:
                category = "公园"
            elif "购物" in activity.title or "商场" in activity.title:
                category = "购物"
            else:
                category = "景点"
            
            print(f"   📂 分类: {category}")
            
            # 获取图片
            try:
                images = get_image_for_activity(
                    activity_name=activity.title,
                    location=destination,
                    category=category
                )
                
                activity.images = images if images else []
                
                if images:
                    print(f"   ✅ 成功添加 {len(images)} 张图片")
                    for i, img in enumerate(images, 1):
                        print(f"      {i}. {img[:80]}...")
                else:
                    print(f"   ⚠️  未找到图片")
                    
            except Exception as e:
                print(f"   ❌ 获取图片失败: {e}")
                activity.images = []
    
    # 检查最终结果
    print("\n" + "="*80)
    print("📊 最终结果:")
    print("="*80)
    
    for daily_plan in mock_itinerary.dailyPlans:
        for activity in daily_plan.activities:
            print(f"\n{activity.title}:")
            if activity.images:
                for i, img in enumerate(activity.images, 1):
                    if 'unsplash' in img:
                        print(f"   ✅ {i}. Unsplash: {img[:60]}...")
                    elif 'pexels' in img:
                        print(f"   ✅ {i}. Pexels: {img[:60]}...")
                    elif 'picsum' in img:
                        print(f"   ❌ {i}. Picsum (占位图!): {img}")
                    else:
                        print(f"   ? {i}. Unknown: {img[:60]}...")
            else:
                print(f"   ⚠️  没有图片")

if __name__ == "__main__":
    test_add_images()
