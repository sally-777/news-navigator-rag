import os
import requests

# محاولة القراءة من streamlit.secrets أولاً (للسيرفر)، ثم من البيئة المحلية
try:
    import streamlit as st
    NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY", ""))
except Exception:
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

def fetch_external_news(query, max_results=5):
    """جلب الأخبار الخارجية عبر Currents API"""
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY is missing in secrets/env!")
        return []

    # رابط طلب الأخبار من Currents API
    url = f"https://api.currentsapi.services/v1/search?keywords={query}&language=en&apiKey={NEWS_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        fetched_docs = []

        if data.get("status") == "ok" and "news" in data:
            articles = data["news"][:max_results]
            for idx, item in enumerate(articles):
                fetched_docs.append({
                    "id": f"currents_doc_{idx}",
                    "title": item.get("title", "External News Title"),
                    "is_current": True,
                    "category": item.get("category", ["general"])[0] if item.get("category") else "general",
                    "url": item.get("url", ""),
                    "text": f"{item.get('title', '')}. {item.get('description', '')}"
                })
        return fetched_docs
    except Exception as e:
        print(f"Error fetching from Currents API: {e}")
        return []
