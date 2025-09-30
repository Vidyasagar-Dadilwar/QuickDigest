import feedparser
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from typing import List, Dict
from datetime import datetime
from .cache import load_cache, save_cache

# Map categories to RSS feed urls (start with English feeds; you can extend later)
CATEGORY_FEEDS = {
    "economics": [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.hindustantimes.com/rss/business/rssfeed.xml",
    ],
    "sports": [
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "https://www.hindustantimes.com/rss/sports/rssfeed.xml"
    ],
    "politics": [
        "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "https://www.thehindu.com/news/national/feeder/default.rss"
    ],
    "technology": [
        "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"  # example
    ],
    "general": [
        "https://timesofindia.indiatimes.com/rssfeeds/-2128905795.cms",
        "https://www.thehindu.com/feeder/default.rss"
    ]
}

def fetch_feed_entries(feed_urls: List[str], limit=30):
    entries = []
    for url in feed_urls:
        parsed = feedparser.parse(url)
        for e in parsed.entries[:limit]:
            entries.append(e)
    return entries

def extract_article_text(url: str) -> str:
    try:
        # try newspaper3k
        art = Article(url)
        art.download()
        art.parse()
        text = art.text
        if text and len(text) > 200:
            return text
    except Exception:
        pass

    # fallback: basic requests + soup
    try:
        r = requests.get(url, headers={"User-Agent":"quickdigest-bot/1.0"}, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # common containers
        content = soup.find("article") or soup.find("div", {"class":"article"}) or soup
        paragraphs = content.find_all("p")
        text = "\n\n".join(p.get_text() for p in paragraphs)
        return text.strip()
    except Exception:
        return ""

def aggregate_category(category: str, refresh: bool = False, max_articles=40):
    """
    Returns list of articles: {title, url, summary(not yet), source, published, text}
    """
    cache = load_cache()
    if cache and not refresh:
        # return cached ones that match category
        cached = [a for a in cache if a.get("category") == category]
        if cached:
            return cached

    feeds = CATEGORY_FEEDS.get(category.lower(), CATEGORY_FEEDS["general"])
    entries = fetch_feed_entries(feeds, limit=40)
    articles = []
    seen = set()
    for e in entries:
        link = e.get("link")
        if not link or link in seen:
            continue
        seen.add(link)
        title = e.get("title", "")
        source = e.get("source", {}).get("title", "") or e.get("publisher", "") or ""
        published = e.get("published", "") or e.get("updated", "")
        text = extract_article_text(link)
        if not text or len(text.split()) < 80:
            continue
        articles.append({
            "title": title,
            "url": link,
            "source": source,
            "published": published,
            "text": text,
            "category": category
        })
        if len(articles) >= max_articles:
            break

    # save in cache (overwrite category subset)
    all_cache = [a for a in load_cache() if a.get("category") != category] + articles
    save_cache(all_cache)
    return articles