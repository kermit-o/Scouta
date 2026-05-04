"""
Fetches trending news from RSS feeds and returns topics for debate.
No API key required.
"""
import feedparser
import random
from datetime import datetime, timezone, timedelta

from app.core.logging import get_logger

log = get_logger(__name__)

RSS_FEEDS = {
    "geopolitics": [
        "https://feeds.reuters.com/reuters/worldNews",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
    "finance": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
    ],
    "technology": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    "politics": [
        "https://rss.politico.com/politics-news.xml",
        "https://feeds.reuters.com/Reuters/PoliticsNews",
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
    ],
}

def fetch_trending_topics(max_per_category: int = 3) -> list[dict]:
    """
    Returns list of trending news items with title, summary, category, source.
    """
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    for category, urls in RSS_FEEDS.items():
        found = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", entry.get("description", "")).strip()
                    link = entry.get("link", "")
                    # Clean summary
                    import re
                    summary = re.sub(r'<[^>]+>', '', summary)[:300]
                    if title and len(title) > 20:
                        found.append({
                            "title": title,
                            "summary": summary,
                            "link": link,
                            "category": category,
                            "source": feed.feed.get("title", url),
                        })
            except Exception as e:
                log.warning("news_fetcher_error", url=url, error=str(e))
                continue

        # Shuffle and take max_per_category
        random.shuffle(found)
        results.extend(found[:max_per_category])

    log.info("news_fetcher_done", topics=len(results))
    return results


def get_debate_prompt_from_news(item: dict) -> tuple[str, str]:
    """
    Returns (title, body_prompt) for generating a debate post from a news item.
    """
    title = item["title"]
    summary = item["summary"]
    category = item["category"]
    source = item["source"]

    body_prompt = f"""Breaking news from {source}:

HEADLINE: {title}

CONTEXT: {summary}

Write a sharp, opinionated essay (400-600 words) analyzing this story from your unique perspective.
Take a strong position. Be provocative. Connect it to bigger patterns you see in the world.
Start directly with your argument — no preamble."""

    return title, body_prompt
