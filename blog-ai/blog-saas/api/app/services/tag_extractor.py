import re
from typing import List

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "how","what","why","when","where","who","which","that","this","these",
    "those","it","its","not","no","so","than","then","do","does","did",
    "will","would","could","should","may","might","can","about","into",
    "through","during","before","after","above","between","each","both",
}

def extract_tags(title: str, body: str, max_tags: int = 5) -> List[str]:
    # 1. Hashtags explícitos en el body
    explicit = [m.group(1).lower() for m in re.finditer(r'#([a-zA-Z][a-zA-Z0-9_]{2,})', body or "")]
    if explicit:
        return list(dict.fromkeys(explicit))[:max_tags]

    # 2. Keywords del título
    words = re.sub(r'[^a-z0-9\s]', '', title.lower()).split()
    keywords = [w for w in words if len(w) > 3 and w not in STOP_WORDS]
    return list(dict.fromkeys(keywords))[:max_tags]


def save_tags_for_post(db, post_id: int, title: str, body: str) -> List[str]:
    from sqlalchemy import text
    tags = extract_tags(title, body)
    for tag in tags:
        try:
            db.execute(text(
                "INSERT INTO post_tags (post_id, tag) VALUES (:post_id, :tag) ON CONFLICT DO NOTHING"
            ), {"post_id": post_id, "tag": tag})
        except Exception:
            pass
    db.commit()
    return tags
