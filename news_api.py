import os
import requests
from dotenv import load_dotenv

load_dotenv()
# يقرأ المفتاح من ملف .env السري
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

def fetch_external_news(query, max_results=5):
    """جلب مقالات حديثة وحقيقية عبر Currents API"""
    if not NEWS_API_KEY or NEWS_API_KEY == "your_news_api_key_here":
        # في حالة عدم وجود المفتاح، يتم إرجاع قائمة فارغة بدلاً من الداتا الوهمية
        print("⚠️ Warning: NEWS_API_KEY is missing or invalid.")
        return []

    # رابط طلب الأخبار الخاص بـ Currents API
    url = f"https://api.currentsapi.services/v1/search?keywords={query}&language=en&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        fetched_docs = []
        
        if data.get("status") == "ok" and "news" in data:
            # اقتطاع أول عدد مقالات مطلوب (max_results)
            articles = data["news"][:max_results]
            for idx, item in enumerate(articles):
                fetched_docs.append({
                    "id": f"currents_doc_{idx}",
                    "title": item.get("title", "External Article"),
                    "is_current": True,
                    "category": item.get("category", ["general"])[0] if item.get("category") else "general",
                    "url": item.get("url", ""), # 👈 تم إضافة رابط المقال الأصلي
                    "text": f"{item.get('title', '')}. {item.get('description', '')}" # 👈 نص المقال كاملاً
                })
        return fetched_docs
    except Exception as e:
        print(f"Error fetching news from Currents API: {e}")
        return []
