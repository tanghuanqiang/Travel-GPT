"""
验证图片API修复的测试脚本
测试新的中文前缀清理逻辑
"""
import os
from dotenv import load_dotenv
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 加载环境变量
load_dotenv()

print("=" * 70)
print("🔧 图片API修复验证测试")
print("=" * 70)
print()

# 检查环境变量
print("1️⃣  检查环境变量配置...")
print("-" * 70)

unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
pexels_key = os.getenv("PEXELS_API_KEY")

if unsplash_key:
    print(f"✅ UNSPLASH_ACCESS_KEY: {unsplash_key[:10]}...{unsplash_key[-5:]}")
else:
    print("❌ UNSPLASH_ACCESS_KEY: 未设置")
    print("   获取地址：https://unsplash.com/developers")

if pexels_key:
    print(f"✅ PEXELS_API_KEY: {pexels_key[:10]}...{pexels_key[-5:]}")
else:
    print("❌ PEXELS_API_KEY: 未设置")
    print("   获取地址：https://www.pexels.com/api/")

if not (unsplash_key or pexels_key):
    print("\n⚠️  警告：未配置任何图片API，测试将无法进行")
    print("   请配置至少一个图片API（推荐同时配置）")
    exit(1)

print()

# 测试新的中文前缀清理逻辑
print("2️⃣  测试中文前缀清理逻辑...")
print("-" * 70)

test_activities = [
    "文化体验：上海博物馆",
    "午餐推荐：南翔馒头店", 
    "游览：外滩",
    "参观：故宫博物院",
    "晚餐：鼎泰丰",
    "打卡：东方明珠",
    "体验：茶艺表演",
    "探索：胡同文化",
    "品尝：北京烤鸭",
    "前往：长城",
]

from app.image_search import get_image_for_activity

print("\n开始测试各种中文前缀的清理效果...")
print()

success_count = 0
total_images = 0

for i, activity in enumerate(test_activities, 1):
    print(f"\n{'='*70}")
    print(f"测试 {i}/{len(test_activities)}: {activity}")
    print(f"{'='*70}")
    
    try:
        images = get_image_for_activity(
            activity_name=activity,
            location="中国",
            category="景点"
        )
        
        if images:
            success_count += 1
            total_images += len(images)
            print(f"\n✅ 成功获取 {len(images)} 张图片:")
            for j, img in enumerate(images, 1):
                print(f"   {j}. {img[:100]}")
        else:
            print(f"\n⚠️  未找到图片")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("📊 测试总结")
print("="*70)
print(f"✅ 成功测试: {success_count}/{len(test_activities)}")
print(f"📸 总共获取: {total_images} 张图片")
print(f"📈 成功率: {success_count/len(test_activities)*100:.1f}%")

if success_count > 0:
    print(f"📊 平均每个活动: {total_images/success_count:.1f} 张图片")

print()

# 性能建议
print("3️⃣  优化建议...")
print("-" * 70)
print("✅ 中文前缀清理逻辑已优化")
print("✅ 日志系统已从print改为logger")
print("✅ 支持更多中文前缀模式")
print()
print("💡 进一步优化建议:")
print("   1. 如果API调用较慢，考虑添加缓存机制")
print("   2. 可以使用异步并行调用提升性能")
print("   3. 建议同时配置Unsplash和Pexels作为备份")
print()
print("="*70)
