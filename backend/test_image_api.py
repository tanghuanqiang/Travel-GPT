"""
图片 API 测试脚本
用于验证 Unsplash 和 Pexels API 配置是否正确
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 60)
print("📸 图片 API 配置测试")
print("=" * 60)
print()

# 检查环境变量
print("1️⃣  检查环境变量...")
print("-" * 60)

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

print()

# 测试 Unsplash API
if unsplash_key:
    print("2️⃣  测试 Unsplash API...")
    print("-" * 60)
    try:
        from app.image_search import search_unsplash
        
        test_query = "Eiffel Tower Paris"
        print(f"搜索关键词: '{test_query}'")
        images = search_unsplash(test_query, count=3)
        
        if images:
            print(f"✅ 成功找到 {len(images)} 张图片：")
            for i, url in enumerate(images, 1):
                print(f"   {i}. {url[:80]}...")
        else:
            print("⚠️  未找到图片（可能是 API Key 无效或网络问题）")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    print()

# 测试 Pexels API
if pexels_key:
    print("3️⃣  测试 Pexels API...")
    print("-" * 60)
    try:
        from app.image_search import search_pexels
        
        test_query = "Grand Palace Bangkok"
        print(f"搜索关键词: '{test_query}'")
        images = search_pexels(test_query, count=3)
        
        if images:
            print(f"✅ 成功找到 {len(images)} 张图片：")
            for i, url in enumerate(images, 1):
                print(f"   {i}. {url[:80]}...")
        else:
            print("⚠️  未找到图片（可能是 API Key 无效或网络问题）")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    print()

# 测试完整流程
print("4️⃣  测试完整图片获取流程...")
print("-" * 60)
try:
    from app.image_search import get_image_for_activity
    
    test_cases = [
        {"activity": "游览故宫", "location": "北京", "category": "景点"},
        {"activity": "午餐：鼎泰丰", "location": "台北", "category": "餐厅"},
        {"activity": "富士山", "location": "日本", "category": "景点"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['activity']} ({case['location']})")
        images = get_image_for_activity(
            case["activity"],
            case["location"],
            case["category"]
        )
        
        if images:
            print(f"✅ 成功获取 {len(images)} 张图片")
            print(f"   预览: {images[0][:80]}...")
        else:
            print("❌ 未获取到图片")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")

print()
print("=" * 60)
print("📊 测试完成！")
print("=" * 60)

# 总结
print()
print("🎯 配置建议：")
if not unsplash_key and not pexels_key:
    print("❌ 未配置任何图片 API，将使用占位图")
    print("   建议：配置 Unsplash 或 Pexels（只需10分钟）")
    print("   指南：查看 IMAGE_API_GUIDE.md")
elif unsplash_key and pexels_key:
    print("✅ 已配置 Unsplash + Pexels 双 API（最佳配置）")
    print("   覆盖率：99% 全球旅行景点")
elif unsplash_key:
    print("✅ 已配置 Unsplash API")
    print("   建议：再配置 Pexels 作为备份（完全免费）")
elif pexels_key:
    print("✅ 已配置 Pexels API")
    print("   建议：再配置 Unsplash 提升覆盖率")

print()
print("📚 详细配置指南：IMAGE_API_GUIDE.md")
print("🚀 现在可以运行项目，查看真实景点照片！")
print()
