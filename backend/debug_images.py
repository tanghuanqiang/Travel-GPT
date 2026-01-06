"""
调试脚本：检查实际生成的行程数据中的图片来源
"""
import json
import sys

# 从命令行读取JSON或从文件读取
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    print("请提供JSON文件路径或粘贴JSON数据")
    print("用法：python debug_images.py <json_file>")
    sys.exit(1)

print("="*70)
print("🔍 分析行程数据中的图片来源")
print("="*70)

total_activities = 0
activities_with_images = 0
picsum_count = 0
unsplash_count = 0
pexels_count = 0
placehold_count = 0
other_count = 0

for day in data.get('dailyPlans', []):
    print(f"\n📅 Day {day['day']}: {day['title']}")
    print("-"*70)
    
    for activity in day.get('activities', []):
        total_activities += 1
        title = activity.get('title', 'Unknown')
        images = activity.get('images', [])
        
        print(f"\n  🎯 {title}")
        
        if images:
            activities_with_images += 1
            print(f"     图片数量: {len(images)}")
            
            for i, img in enumerate(images, 1):
                print(f"     {i}. {img[:100]}...")
                
                # 分析图片来源
                if 'picsum.photos' in img:
                    picsum_count += 1
                    print(f"        ❌ picsum占位图")
                elif 'images.unsplash.com' in img or 'source.unsplash.com' in img:
                    unsplash_count += 1
                    print(f"        ✅ Unsplash真实图片")
                elif 'images.pexels.com' in img:
                    pexels_count += 1
                    print(f"        ✅ Pexels真实图片")
                elif 'placehold' in img or 'placeholder' in img:
                    placehold_count += 1
                    print(f"        ❌ 占位图")
                else:
                    other_count += 1
                    print(f"        ⚠️  其他来源")
        else:
            print(f"     ❌ 无图片")

print("\n"+"="*70)
print("📊 统计结果")
print("="*70)
print(f"总活动数: {total_activities}")
print(f"有图片的活动: {activities_with_images}")
print(f"")
print(f"图片来源分析:")
print(f"  ❌ Picsum占位图: {picsum_count}")
print(f"  ❌ Placeholder占位图: {placehold_count}")
print(f"  ✅ Unsplash真实图片: {unsplash_count}")
print(f"  ✅ Pexels真实图片: {pexels_count}")
print(f"  ⚠️  其他来源: {other_count}")
print(f"")

if picsum_count > 0 or placehold_count > 0:
    print("⚠️  警告：发现占位图！")
    print("")
    print("可能的原因:")
    print("1. LLM在生成JSON时包含了images字段（包含占位图）")
    print("2. 后端的图片替换逻辑未正确执行")
    print("3. Unsplash/Pexels API未正确配置或调用失败")
    print("")
    print("建议:")
    print("1. 检查后端日志，确认_add_images_to_itinerary()是否被调用")
    print("2. 检查Unsplash/Pexels API配置（.env文件）")
    print("3. 运行test_fix_verification.py测试API连接")
else:
    print("✅ 未发现占位图，所有图片均来自真实API")
