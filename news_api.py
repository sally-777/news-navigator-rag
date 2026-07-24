import os
import requests
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

def fetch_external_news(query, max_results=5):
    """جلب مقالات حديثة عبر الـ API وتنسيقها كـ Dictionaries"""
    if not NEWS_API_KEY or NEWS_API_KEY == "your_news_api_key_here":
        # محاكاة لنتائج جلب الأخبار
        return [{
            "id": f"api_{query[:5]}_01",
            "title": f"Live News Update: {query}",
            "is_current": True,
            "category": "live_news",
            "text": f"Latest external article retrieved about {query}. Recent breaking details regarding this topic."
        }]

    url = f"https://newsapi.org/v2/everything?q={query}&pageSize={max_results}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        fetched_docs = []
        if data.get("status") == "ok":
            for idx, item in enumerate(data.get("articles", [])):
                fetched_docs.append({
                    "id": f"api_doc_{idx}",
                    "title": item.get("title", "External Article"),
                    "is_current": True,
                    "category": "live_news",
                    "text": f"{item.get('title', '')}. {item.get('description', '')} {item.get('content', '')}"
                })
        return fetched_docs
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []