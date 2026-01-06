"""
图片搜索工具 - 使用 Unsplash + Pexels API 获取真实旅行照片

支持的 API：
1. Unsplash API (推荐首选) - 数百万专业旅行照片
2. Pexels API (并列首选) - 完全免费无限请求

API 获取指南：
- Unsplash: https://unsplash.com/developers (免费 50 requests/hour)
- Pexels: https://www.pexels.com/api/ (完全免费无限制)
"""
import os
import urllib.parse
import requests
from typing import List, Optional
import time


def get_image_for_activity(activity_name: str, location: str = "", category: str = "") -> List[str]:
    """
    根据活动名称和位置获取真实景点图片（优先使用 Unsplash/Pexels API）
    
    Args:
        activity_name: 活动名称，如"故宫"、"南翔馒头店"
        location: 位置，如"北京"、"上海"
        category: 类别，如"景点"、"餐厅"、"酒店"
    
    Returns:
        图片URL列表（2-3张真实照片），如果找不到相关图片返回空列表
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🔍 get_image_for_activity 被调用")
    logger.info(f"   输入参数:")
    logger.info(f"   - activity_name: {activity_name}")
    logger.info(f"   - location: {location}")
    logger.info(f"   - category: {category}")
    logger.info(f"{'='*70}")
    
    import re
    clean_name = activity_name
    
    # 移除常见的中文前缀和动词
    prefixes_to_remove = [
        r'^游览[:：]?',
        r'^参观[:：]?',
        r'^打卡[:：]?',
        r'^体验[:：]?',
        r'^探索[:：]?',
        r'^午餐[:：]?',
        r'^晚餐[:：]?',
        r'^早餐[:：]?',
        r'^美食[:：]?',
        r'^文化体验[:：]?',
        r'^午餐推荐[:：]?',
        r'^晚餐推荐[:：]?',
        r'^品尝[:：]?',
        r'^前往[:：]?',
        r'^到达[:：]?',
        r'^伴手礼采购[:：]?',
    ]
    
    for pattern in prefixes_to_remove:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
    
    # 移除括号内的店铺信息，如"（中央大街店）"
    clean_name = re.sub(r'[（(][^）)]*[店铺馆厅][）)]', '', clean_name)
    clean_name = clean_name.strip()
    
    print(f"📝 清理后的名称: '{clean_name}'")
    
    # 智能分类检测
    activity_lower = activity_name.lower()
    if not category or category not in ["景点", "餐厅", "美食", "酒店", "公园", "博物馆", "寺庙", "古镇", "夜景", "购物"]:
        if any(word in activity_lower for word in ['餐', '饭', '吃', '食', '厅', '馆', '铺', '包', '饺', '面', '菜', '锅', '烤', '炖']):
            category = "美食"
        elif any(word in activity_lower for word in ['博物']):
            category = "博物馆"
        elif any(word in activity_lower for word in ['寺', '庙', '宫', '文庙']):
            category = "寺庙"
        elif any(word in activity_lower for word in ['公园', '花园']):
            category = "公园"
        elif any(word in activity_lower for word in ['购物', '商场', '商城', '专卖']):
            category = "购物"
        elif any(word in activity_lower for word in ['酒店', '宾馆', '民宿']):
            category = "酒店"
        else:
            category = "景点"
    
    # 根据类别构建更智能的搜索策略
    def build_search_queries(name: str, loc: str, cat: str) -> List[str]:
        """构建多个搜索查询，从具体到通用"""
        queries = []
        
        # 美食类别：使用菜品类型而非餐厅名
        if cat in ["美食", "餐厅"]:
            # 提取菜品关键词
            food_keywords = extract_food_keywords(name, loc)
            if food_keywords:
                queries.append(f"{food_keywords} food dish")
            # 添加地方菜系
            if loc:
                regional_cuisine = get_regional_cuisine(loc)
                if regional_cuisine:
                    queries.append(f"{regional_cuisine} cuisine food")
            # 通用美食
            queries.append(f"Chinese food dish cuisine")
        
        # 景点类别
        elif cat == "景点":
            # 先尝试具体景点名 + 城市
            if loc:
                queries.append(f"{name} {loc} landmark")
            queries.append(f"{name} travel attraction")
            # 如果是著名景点，只用名字
            if is_famous_landmark(name):
                queries.append(f"{name}")
        
        # 博物馆
        elif cat == "博物馆":
            queries.append(f"{name} museum")
            if loc:
                queries.append(f"{loc} museum gallery")
        
        # 寺庙
        elif cat == "寺庙":
            queries.append(f"{name} temple")
            if loc:
                queries.append(f"{loc} temple shrine")
            queries.append("Chinese temple architecture")
        
        # 购物
        elif cat == "购物":
            if loc:
                queries.append(f"{loc} shopping mall")
            queries.append("shopping mall retail store")
        
        # 公园
        elif cat == "公园":
            queries.append(f"{name} park")
            if loc:
                queries.append(f"{loc} park garden nature")
        
        # 默认
        else:
            if loc:
                queries.append(f"{name} {loc}")
            queries.append(f"{name} travel")
        
        return queries
    
    queries = build_search_queries(clean_name, location, category)
    logger.info(f"🔎 搜索策略: {queries}")
    logger.info(f"{'-'*70}")
    
    images = []
    
    # 尝试每个查询直到获得足够的图片
    for i, query in enumerate(queries):
        if len(images) >= 3:
            break
            
        logger.info(f"\n📸 尝试查询 {i+1}/{len(queries)}: '{query}'")
        
        # 先尝试 Unsplash
        unsplash_images = search_unsplash(query, count=3 - len(images))
        if unsplash_images:
            images.extend(unsplash_images)
            logger.info(f"   Unsplash: 获得 {len(unsplash_images)} 张")
        
        # 如果还不够，尝试 Pexels
        if len(images) < 3:
            pexels_images = search_pexels(query, count=3 - len(images))
            if pexels_images:
                # 过滤重复图片
                for img in pexels_images:
                    if img not in images:
                        images.append(img)
                logger.info(f"   Pexels: 获得 {len(pexels_images)} 张")
    
    # 去重
    images = list(dict.fromkeys(images))
    
    final_count = len(images)
    logger.info(f"\n{'='*70}")
    if images:
        logger.info(f"✅ 最终结果: 成功获取 {final_count} 张图片")
        for i, img in enumerate(images[:3], 1):
            logger.info(f"   {i}. {img[:100]}...")
    else:
        logger.warning(f"⚠️  最终结果: 未找到相关图片（返回空数组）")
    logger.info(f"{'='*70}\n")
    
    return images[:3] if images else []


def extract_food_keywords(name: str, location: str) -> str:
    """从餐厅名称中提取菜品关键词"""
    food_patterns = {
        '饺子': 'dumplings chinese',
        '包子': 'baozi steamed bun',
        '馒头': 'mantou steamed bun',
        '春饼': 'spring pancake chinese',
        '烤肉': 'korean bbq grilled meat',
        '火锅': 'hotpot chinese',
        '铁锅炖': 'stew chinese casserole',
        '砂锅': 'clay pot stew',
        '西餐': 'western food steak',
        '俄罗斯': 'russian food cuisine',
        '红肠': 'sausage harbin',
        '锅包肉': 'sweet sour pork chinese',
        '小笼': 'xiaolongbao soup dumplings',
        '面': 'noodles chinese',
        '粥': 'congee rice porridge',
        '烧烤': 'bbq grilled',
        '海鲜': 'seafood',
        '川菜': 'sichuan spicy food',
        '粤菜': 'cantonese dim sum',
        '东北菜': 'northeastern chinese food',
    }
    
    for keyword, english in food_patterns.items():
        if keyword in name:
            return english
    
    return ""


def get_regional_cuisine(location: str) -> str:
    """根据城市获取地方菜系"""
    cuisine_map = {
        '哈尔滨': 'northeastern chinese Harbin',
        '上海': 'shanghai cuisine',
        '北京': 'beijing peking food',
        '成都': 'sichuan spicy food',
        '广州': 'cantonese dim sum',
        '西安': 'xian food noodles',
        '重庆': 'chongqing hotpot spicy',
        '杭州': 'hangzhou cuisine',
        '南京': 'jiangsu cuisine',
        '长沙': 'hunan spicy food',
    }
    return cuisine_map.get(location, "chinese food")


def is_famous_landmark(name: str) -> bool:
    """检查是否是著名景点"""
    famous = [
        '故宫', '长城', '天安门', '外滩', '东方明珠', '西湖', '兵马俑',
        '布达拉宫', '九寨沟', '黄山', '张家界', '颐和园', '天坛',
        '圣索菲亚', '中央大街', '太阳岛', '冰雪大世界',
    ]
    return any(f in name for f in famous)


def get_image_for_location(location: str, image_type: str = "cityscape") -> str:
    """
    获取目的地的城市景观图片（优先使用真实 API）
    
    Args:
        location: 城市名称，如"上海"、"北京"
        image_type: 图片类型，如"cityscape"、"landscape"、"architecture"
    
    Returns:
        图片URL
    """
    query = f"{location} {image_type} travel"
    
    # 优先 Unsplash
    images = search_unsplash(query, count=1)
    if images:
        return images[0]
    
    # 备用 Pexels
    images = search_pexels(query, count=1)
    if images:
        return images[0]
    
    # 如果都没有找到，返回空字符串（不使用占位图）
    return ""


def search_unsplash(query: str, count: int = 3) -> List[str]:
    """
    使用 Unsplash API 搜索真实旅行照片
    
    获取 API Key：
    1. 访问 https://unsplash.com/developers
    2. 点击 "Register as a developer"
    3. 创建应用 (New Application)
    4. 复制 Access Key
    5. 在 .env 文件中设置: UNSPLASH_ACCESS_KEY=your_access_key
    
    免费限额：50 requests/hour（可申请提升到 5000/hour）
    
    Args:
        query: 搜索关键词（如 "Eiffel Tower Paris landmark"）
        count: 返回图片数量
    
    Returns:
        图片URL列表（regular 尺寸，约 1080px）
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"\n🔵 [Unsplash API] 开始调用")
    logger.debug(f"   查询: '{query}'")
    logger.debug(f"   数量: {count}")
    
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        logger.warning("   ❌ 未设置 UNSPLASH_ACCESS_KEY")
        logger.info("   💡 请访问 https://unsplash.com/developers 获取")
        return []
    
    logger.debug(f"   ✓ API Key 已配置: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {api_key}"
        }
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape",  # 横向图片更适合旅行卡片
            "content_filter": "high"     # 高质量过滤
        }
        
        logger.debug(f"   📡 发送请求到: {url}")
        logger.debug(f"   📦 请求参数: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        logger.debug(f"   📨 响应状态码: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        total = data.get("total", 0)
        
        logger.debug(f"   📊 API返回: total={total}, results={len(results)}")
        
        # 返回 regular 尺寸（约1080px），适合网页显示
        images = [photo["urls"]["regular"] for photo in results]
        
        if images:
            logger.debug(f"   ✅ 成功获取 {len(images)} 张图片")
            for i, img in enumerate(images[:2], 1):
                logger.debug(f"      {i}. {img[:80]}...")
        else:
            logger.debug(f"   ⚠️  未找到图片")
        
        return images
    
    except requests.exceptions.Timeout:
        logger.warning(f"   ❌ 请求超时 (>10秒)")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"   ❌ 网络请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"   响应内容: {e.response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"   ❌ 处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def search_pexels(query: str, count: int = 3) -> List[str]:
    """
    使用 Pexels API 搜索真实旅行照片（完全免费）
    
    获取 API Key：
    1. 访问 https://www.pexels.com/api/
    2. 点击 "Get Started" 或 "Your API Key"
    3. 免费注册账号
    4. 复制 API Key
    5. 在 .env 文件中设置: PEXELS_API_KEY=your_api_key
    
    免费限额：200 requests/hour, 20,000/month（完全免费！）
    
    Args:
        query: 搜索关键词（如 "Grand Palace Bangkok hotel"）
        count: 返回图片数量
    
    Returns:
        图片URL列表（large 尺寸）
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"\n🟢 [Pexels API] 开始调用")
    logger.debug(f"   查询: '{query}'")
    logger.debug(f"   数量: {count}")
    
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        logger.warning("   ❌ 未设置 PEXELS_API_KEY")
        logger.info("   💡 请访问 https://www.pexels.com/api/ 获取")
        return []
    
    logger.debug(f"   ✓ API Key 已配置: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": api_key
        }
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape"
        }
        
        logger.debug(f"   📡 发送请求到: {url}")
        logger.debug(f"   📦 请求参数: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        logger.debug(f"   📨 响应状态码: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        photos = data.get("photos", [])
        total = data.get("total_results", 0)
        
        logger.debug(f"   📊 API返回: total_results={total}, photos={len(photos)}")
        
        # 返回 large 尺寸图片
        images = [photo["src"]["large"] for photo in photos]
        
        if images:
            logger.debug(f"   ✅ 成功获取 {len(images)} 张图片")
            for i, img in enumerate(images[:2], 1):
                logger.debug(f"      {i}. {img[:80]}...")
        else:
            logger.debug(f"   ⚠️  未找到图片")
        
        return images
    
    except requests.exceptions.Timeout:
        logger.warning(f"   ❌ 请求超时 (>10秒)")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"   ❌ 网络请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"   响应内容: {e.response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"   ❌ 处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def get_placeholder_images(text: str, count: int = 3) -> List[str]:
    """
    获取占位图（当 API 不可用时的备用方案）
    
    Args:
        text: 显示文本
        count: 图片数量
    
    Returns:
        占位图URL列表
    """
    encoded_text = urllib.parse.quote(text[:20])  # 限制长度
    base_url = f"https://placehold.co/800x600/3b82f6/ffffff?text={encoded_text}"
    
    # 使用不同颜色生成多张占位图
    colors = ["3b82f6", "8b5cf6", "ec4899", "f59e0b", "10b981"]
    images = []
    
    for i in range(count):
        color = colors[i % len(colors)]
        images.append(f"https://placehold.co/800x600/{color}/ffffff?text={encoded_text}")
    
    return images
