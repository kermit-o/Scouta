import bleach
import markdown as md

ALLOWED_TAGS = [
    "p", "br", "hr",
    "strong", "em", "code", "pre",
    "h1", "h2", "h3", "h4",
    "ul", "ol", "li",
    "blockquote",
    "a",
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
}

def render_markdown_safe(text: str) -> str:
    html = md.markdown(text or "", extensions=["fenced_code", "tables"])
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    clean = bleach.linkify(clean)
    return clean
