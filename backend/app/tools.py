"""
External API Tools for TravelPlanGPT
集成各种外部API用于搜索景点、餐厅、图片等
"""
import os
import requests
from typing import List, Dict, Any


def search_attractions(city: str) -> str:
    """
    搜索城市的景点信息
    
    Args:
        city: 城市名称
    
    Returns:
        景点信息的JSON字符串
    """
    # 这里可以集成Google Places API或其他景点API
    # 现在返回示例数据
    
    mock_data = {
        "attractions": [
            {
                "name": f"{city}博物馆",
                "rating": 4.5,
                "description": "展示城市历史文化的重要博物馆",
                "category": "文化",
                "price": "免费",
                "popular": True
            },
            {
                "name": f"{city}老街",
                "rating": 4.3,
                "description": "保留传统建筑的历史街区",
                "category": "历史",
                "price": "免费",
                "popular": True
            },
            {
                "name": "本地艺术画廊",
                "rating": 4.7,
                "description": "展示当代艺术作品的小众画廊",
                "category": "艺术",
                "price": "30元",
                "popular": False
            }
        ]
    }
    
    return str(mock_data)


def search_restaurants(query: str) -> str:
    """
    搜索餐厅信息
    
    Args:
        query: 搜索关键词（城市+美食类型）
    
    Returns:
        餐厅信息的JSON字符串
    """
    # 可以集成Yelp API、Google Places API等
    
    mock_data = {
        "restaurants": [
            {
                "name": "本地特色餐厅",
                "rating": 4.6,
                "cuisine": "本帮菜",
                "priceRange": "¥¥",
                "specialties": ["特色小笼包", "红烧肉"],
                "address": "市中心XX路123号"
            },
            {
                "name": "隐藏小吃店",
                "rating": 4.8,
                "cuisine": "街头小吃",
                "priceRange": "¥",
                "specialties": ["烤串", "炒面"],
                "address": "老城区巷子里",
                "hidden_gem": True
            }
        ]
    }
    
    return str(mock_data)


def get_place_images(place_name: str, count: int = 3) -> List[str]:
    """
    获取地点的真实图片URL（使用 Unsplash + Pexels API）
    
    Args:
        place_name: 地点名称（如 "Eiffel Tower Paris" 或 "故宫 北京"）
        count: 需要的图片数量
    
    Returns:
        图片URL列表（真实高质量照片）
    """
    from app.image_search import search_unsplash, search_pexels, get_placeholder_images
    
    # 优化搜索关键词：添加 "travel" 或 "landmark" 提升相关性
    enhanced_query = f"{place_name} travel landmark"
    
    # 优先尝试 Unsplash API
    images = search_unsplash(enhanced_query, count=count)
    
    # 如果 Unsplash 结果不够，补充 Pexels
    if len(images) < count:
        remaining = count - len(images)
        pexels_images = search_pexels(enhanced_query, count=remaining)
        images.extend(pexels_images)
    
    # 如果没有找到图片，返回空数组（不使用占位图）
    if not images:
        print(f"⚠️  未找到 '{place_name}' 的真实图片")
    
    return images[:count] if images else []


def get_weather_info(city: str) -> str:
    """
    获取城市天气信息
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息字符串
    """
    # 可以集成OpenWeatherMap API
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if api_key:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric",
                "lang": "zh_cn"
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                return f"{city}当前温度{temp}°C，{description}。建议准备相应的衣物。"
        except Exception as e:
            print(f"Error fetching weather: {e}")
    
    # Fallback
    return f"{city}天气宜人，建议带好防晒用品和雨具以备不时之需。"


def search_hidden_gems(city: str, preferences: List[str]) -> str:
    """
    搜索隐藏的小众景点
    
    Args:
        city: 城市名称
        preferences: 用户偏好列表
    
    Returns:
        隐藏景点信息
    """
    # 可以使用Tavily或专门的本地探索API
    
    mock_data = {
        "hidden_gems": [
            {
                "name": "本地人咖啡馆",
                "description": "只有本地人知道的精品咖啡店，下午常有爵士乐演出",
                "category": "咖啡文化",
                "why_special": "氛围独特，价格亲民，远离游客区"
            },
            {
                "name": "屋顶酒吧",
                "description": "隐藏在老建筑顶层的酒吧，可以俯瞰城市夜景",
                "category": "夜生活",
                "why_special": "本地年轻人聚集地，景观绝佳"
            }
        ]
    }
    
    return str(mock_data)


def calculate_route_time(origin: str, destination: str) -> Dict[str, Any]:
    """
    计算两地之间的交通时间
    
    Args:
        origin: 起点
        destination: 终点
    
    Returns:
        交通信息字典
    """
    # 可以集成Google Maps Distance Matrix API
    
    return {
        "duration": "15分钟",
        "distance": "3公里",
        "mode": "地铁或步行",
        "cost": 5
    }
