"""
直接测试图片 API 是否工作
"""
import sys
sys.path.insert(0, 'D:\\gitRepositories\\Travel-GPT\\backend')

from app.image_search import search_unsplash, search_pexels, get_image_for_activity
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("\n" + "="*70)
print("🧪 开始测试图片 API")
print("="*70)

# 检查环境变量
print("\n1️⃣ 检查 API Keys 配置:")
print("-"*70)
unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
pexels_key = os.getenv("PEXELS_API_KEY")

if unsplash_key:
    print(f"✅ UNSPLASH_ACCESS_KEY: {unsplash_key[:10]}...{unsplash_key[-5:]}")
else:
    print("❌ UNSPLASH_ACCESS_KEY: 未配置")

if pexels_key:
    print(f"✅ PEXELS_API_KEY: {pexels_key[:10]}...{pexels_key[-5:]}")
else:
    print("❌ PEXELS_API_KEY: 未配置")

# 测试 Unsplash
print("\n2️⃣ 测试 Unsplash API:")
print("-"*70)
try:
    images = search_unsplash("Paris Eiffel Tower", count=2)
    if images:
        print(f"✅ 成功获取 {len(images)} 张图片:")
        for i, img in enumerate(images, 1):
            print(f"   {i}. {img}")
    else:
        print("❌ 未获取到图片")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 Pexels
print("\n3️⃣ 测试 Pexels API:")
print("-"*70)
try:
    images = search_pexels("Tokyo Japan", count=2)
    if images:
        print(f"✅ 成功获取 {len(images)} 张图片:")
        for i, img in enumerate(images, 1):
            print(f"   {i}. {img}")
    else:
        print("❌ 未获取到图片")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试完整流程
print("\n4️⃣ 测试完整流程 (get_image_for_activity):")
print("-"*70)
try:
    images = get_image_for_activity("外滩", "上海", "景点")
    if images:
        print(f"✅ 成功获取 {len(images)} 张图片:")
        for i, img in enumerate(images, 1):
            print(f"   {i}. {img}")
    else:
        print("❌ 未获取到图片")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ 测试完成")
print("="*70)
