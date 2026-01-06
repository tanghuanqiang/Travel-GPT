"""测试 Unsplash 和 Pexels API"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_unsplash():
    print("="*60)
    print("测试 Unsplash API")
    print("="*60)
    
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        print("❌ UNSPLASH_ACCESS_KEY 未设置")
        return
    
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": "Shanghai Bund landmark travel", "per_page": 3}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总结果: {data.get('total', 0)}")
            results = data.get('results', [])
            print(f"返回数量: {len(results)}")
            for i, photo in enumerate(results[:3]):
                print(f"{i+1}. {photo['urls']['regular'][:100]}...")
        else:
            print(f"错误响应: {response.text[:300]}")
    except Exception as e:
        print(f"错误: {e}")

def test_pexels():
    print("\n" + "="*60)
    print("测试 Pexels API")
    print("="*60)
    
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("❌ PEXELS_API_KEY 未设置")
        return
    
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": api_key}
        params = {"query": "Shanghai Bund landmark travel", "per_page": 3}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总结果: {data.get('total_results', 0)}")
            photos = data.get('photos', [])
            print(f"返回数量: {len(photos)}")
            for i, photo in enumerate(photos[:3]):
                print(f"{i+1}. {photo['src']['large'][:100]}...")
        else:
            print(f"错误响应: {response.text[:300]}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_unsplash()
    test_pexels()
