"use client";

function extractHashtags(title: string, body: string): string[] {
  const explicit = Array.from(body.matchAll(/#([a-zA-Z][a-zA-Z0-9_]{2,})/g))
    .map((m) => m[1].toLowerCase());

  if (explicit.length > 0) {
    return [...new Set(explicit)].slice(0, 6);
  }

  const stopWords = new Set([
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "how","what","why","when","where","who","which","that","this","not",
  ]);

  const words = title
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .split(/\s+/)
    .filter((w) => w.length > 3 && !stopWords.has(w));

  return [...new Set(words)].slice(0, 5);
}

interface Props {
  title: string;
  body: string;
}

export default function HashtagRow({ title, body }: Props) {
  const tags = extractHashtags(title, body || "");
  if (tags.length === 0) return null;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", margin: "0.75rem 0 1rem" }}>
      {tags.map((tag) => (
        
          key={tag}
          href={"/posts?tag=" + tag}
          style={{
            fontSize: "0.65rem",
            fontFamily: "monospace",
            letterSpacing: "0.05em",
            color: "#4a7a9a",
            background: "#0d1a22",
            border: "1px solid #1a3a4a",
            padding: "0.2rem 0.6rem",
            textDecoration: "none",
          }}
        >
          {"#" + tag}
        </a>
      ))}
    </div>
  );
}
