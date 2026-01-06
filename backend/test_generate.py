"""测试 generate-plan 接口"""
import requests
import json

print('发送测试请求到 /api/generate-plan...')
print('(这可能需要 30-60 秒)')

try:
    response = requests.post(
        'http://localhost:8000/api/generate-plan',
        json={
            'destination': '上海',
            'days': 1,
            'budget': '3000',
            'travelers': 1,
            'preferences': ['美食']
        },
        timeout=120
    )

    print(f'\n状态码: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('\n' + '='*60)
        print('检查返回的 images:')
        print('='*60)
        
        unsplash_count = 0
        pexels_count = 0
        picsum_count = 0
        empty_count = 0
        
        for day in data.get('dailyPlans', []):
            print(f'\nDay {day.get("day")}:')
            for activity in day.get('activities', []):
                title = activity.get('title', 'Unknown')
                images = activity.get('images', [])
                print(f'\n  📍 {title}: {len(images)} 张图片')
                
                if not images:
                    empty_count += 1
                    print(f'    ⚠️  没有图片')
                
                for img in images[:3]:
                    if 'unsplash' in img:
                        unsplash_count += 1
                        print(f'    ✅ Unsplash: {img[:70]}...')
                    elif 'pexels' in img:
                        pexels_count += 1
                        print(f'    ✅ Pexels: {img[:70]}...')
                    elif 'picsum' in img:
                        picsum_count += 1
                        print(f'    ❌ Picsum: {img}')
                    else:
                        print(f'    ? Unknown: {img[:70]}...')
        
        print('\n' + '='*60)
        print('📊 统计结果:')
        print('='*60)
        print(f'  ✅ Unsplash 图片: {unsplash_count}')
        print(f'  ✅ Pexels 图片: {pexels_count}')
        print(f'  ❌ Picsum 占位图: {picsum_count}')
        print(f'  ⚠️  无图片活动: {empty_count}')
        
        if picsum_count > 0:
            print('\n❌ 问题仍然存在: 还有 Picsum 占位图!')
        elif unsplash_count + pexels_count > 0:
            print('\n✅ 修复成功: 所有图片都来自 Unsplash/Pexels!')
        else:
            print('\n⚠️  没有获取到任何图片')
            
    else:
        print(f'错误: {response.text[:500]}')
        
except requests.exceptions.Timeout:
    print('请求超时 (120秒)')
except Exception as e:
    print(f'错误: {e}')
