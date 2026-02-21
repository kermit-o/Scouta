"use client";
import Link from "next/link";

interface Props {
  tags?: string[];
  title?: string;
  body?: string;
}

function extractFromTitle(title: string): string[] {
  const stopWords = new Set([
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "how","what","why","when","where","who","which","that","this","not",
  ]);
  const words = title.toLowerCase().replace(/[^a-z0-9\s]/g, "").split(/\s+/)
    .filter((w) => w.length > 3 && !stopWords.has(w));
  return [...new Set(words)].slice(0, 5);
}

export default function HashtagRow({ tags, title, body }: Props) {
  const displayTags = tags && tags.length > 0
    ? tags
    : title ? extractFromTitle(title) : [];

  if (displayTags.length === 0) return null;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", margin: "0.5rem 0 1rem" }}>
      {displayTags.map((tag) => (
        <Link
          key={tag}
          href={"/posts?tag=" + tag}
          style={{
            fontSize: "0.62rem", fontFamily: "monospace", letterSpacing: "0.05em",
            color: "#4a7a9a", background: "#0d1a22", border: "1px solid #1a3a4a",
            padding: "0.15rem 0.5rem", textDecoration: "none",
          }}
        >
          {"#" + tag}
        </Link>
      ))}
    </div>
  );
}
