"""模拟 FastAPI 异步环境下的行为"""
import asyncio
import os
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

from app.models import TravelRequest, Activity, DailyPlan, TravelItinerary, BudgetOverview, HiddenGem, PracticalTips
from app.image_search import get_image_for_activity


def add_images_to_itinerary_sync(itinerary: TravelItinerary, destination: str) -> TravelItinerary:
    """模拟 agent.py 中的 _add_images_to_itinerary 方法"""
    
    logger.info("\n" + "="*60)
    logger.info("🖼️  开始为活动添加真实图片...")
    logger.info("="*60)
    
    # 🔧 第一步：强制清除所有LLM可能生成的图片
    logger.info("🧹 第一步：清除所有现有图片...")
    cleaned_count = 0
    for daily_plan in itinerary.dailyPlans:
        for activity in daily_plan.activities:
            if hasattr(activity, 'images') and activity.images:
                old_images = activity.images.copy()
                activity.images = []
                cleaned_count += 1
                logger.warning(f"   ⚠️  清除了 '{activity.title}' 的 {len(old_images)} 张图片:")
                for img in old_images[:1]:
                    if 'picsum' in img or 'placeholder' in img or 'placehold' in img:
                        logger.warning(f"      ❌ 占位图: {img[:60]}...")
                    else:
                        logger.info(f"      🗑️  其他: {img[:60]}...")
    
    if cleaned_count > 0:
        logger.info(f"✅ 已清除 {cleaned_count} 个活动的原有图片")
    else:
        logger.info(f"✅ 无需清除（LLM未生成图片）")
    logger.info("")
    
    async def fetch_images_for_activity(activity, destination, day_num, activity_idx):
        """异步获取单个活动的图片"""
        try:
            category = "景点"
            if "餐" in activity.title or "吃" in activity.title or "美食" in activity.title:
                category = "美食"
            
            logger.debug(f"🎯 [Day{day_num}-{activity_idx}] {activity.title} (类型: {category})")
            
            images = get_image_for_activity(
                activity_name=activity.title,
                location=destination,
                category=category
            )
            
            activity.images = images if images else []
            
            if images:
                logger.debug(f"✅ [Day{day_num}-{activity_idx}] 成功添加 {len(images)} 张图片")
            else:
                logger.warning(f"⚠️  [Day{day_num}-{activity_idx}] 未找到图片")
                
        except Exception as e:
            logger.error(f"❌ [Day{day_num}-{activity_idx}] 获取图片失败: {e}")
            activity.images = []
    
    async def process_all_activities():
        """并行处理所有活动的图片获取"""
        for daily_plan in itinerary.dailyPlans:
            for idx, activity in enumerate(daily_plan.activities, 1):
                await fetch_images_for_activity(activity, destination, daily_plan.day, idx)
        
    # 运行异步任务
    print("\n🔴 尝试 asyncio.run()...")
    try:
        asyncio.run(process_all_activities())
        print("✅ asyncio.run() 成功")
    except RuntimeError as e:
        print(f"⚠️  asyncio.run() 失败 (RuntimeError): {e}")
        print("🟡 切换到同步模式...")
        # 如果已经在事件循环中，使用同步方式
        for daily_plan in itinerary.dailyPlans:
            logger.info(f"\n📅 Day {daily_plan.day}: {daily_plan.title}")
            logger.info("-" * 60)
            
            for idx, activity in enumerate(daily_plan.activities, 1):
                logger.info(f"\n🎯 处理活动 {idx}: {activity.title}")
                
                category = "景点"
                if "餐" in activity.title or "吃" in activity.title or "美食" in activity.title:
                    category = "美食"
                
                try:
                    images = get_image_for_activity(
                        activity_name=activity.title,
                        location=destination,
                        category=category
                    )
                    
                    activity.images = images if images else []
                    
                    if images:
                        logger.info(f"   ✅ 成功添加 {len(images)} 张图片")
                    else:
                        logger.warning(f"   ⚠️  未找到图片（将不显示图片）")
                        
                except Exception as e:
                    logger.error(f"   ❌ 获取图片失败: {e}")
                    activity.images = []
    except Exception as e:
        print(f"❌ 未捕获的异常类型 ({type(e).__name__}): {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "="*60)
    logger.info("✅ 图片添加完成！")
    logger.info("="*60 + "\n")
    
    return itinerary


async def simulate_fastapi_request():
    """模拟 FastAPI 的异步请求环境"""
    print("\n" + "="*80)
    print("🌐 模拟 FastAPI 异步环境")
    print("="*80)
    
    # 创建模拟的行程数据（模拟 LLM 生成了 picsum 图片）
    mock_activities = [
        Activity(
            time="09:00",
            title="外滩",
            description="免费活动...",
            duration="1.5小时",
            cost=0.0,
            address="黄浦区中山东一路",
            reason="上海地标",
            images=["https://picsum.photos/800/600?random=1"]  # 模拟 LLM 生成的占位图
        )
    ]
    
    mock_daily_plan = DailyPlan(
        day=1,
        title="Day 1: 上海一日游",
        activities=mock_activities
    )
    
    mock_itinerary = TravelItinerary(
        overview=BudgetOverview(totalBudget=3000.0, budgetBreakdown=[]),
        dailyPlans=[mock_daily_plan],
        hiddenGems=[],
        practicalTips=PracticalTips(
            transportation="地铁",
            packingList=["舒适鞋子"],
            weather="晴朗",
            seasonalNotes="注意防晒"
        )
    )
    
    print(f"📋 初始状态: {mock_activities[0].images}")
    
    # 调用同步函数（这会在事件循环中触发 RuntimeError）
    result = add_images_to_itinerary_sync(mock_itinerary, "上海")
    
    print("\n📊 最终结果:")
    for daily_plan in result.dailyPlans:
        for activity in daily_plan.activities:
            print(f"   {activity.title}: {len(activity.images)} 张图片")
            for img in activity.images[:2]:
                if 'unsplash' in img:
                    print(f"      ✅ Unsplash")
                elif 'pexels' in img:
                    print(f"      ✅ Pexels")
                elif 'picsum' in img:
                    print(f"      ❌ Picsum (占位图!)")


if __name__ == "__main__":
    # 使用 asyncio.run 来模拟 FastAPI 的环境
    asyncio.run(simulate_fastapi_request())
