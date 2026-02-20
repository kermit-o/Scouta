"use client";

import ReactMarkdown from "react-markdown";

export default function MarkdownBody({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        h1: ({ children }) => <h1 style={{ fontSize: "1.6rem", fontWeight: 400, color: "#f0e8d8", margin: "1.5rem 0 0.75rem", lineHeight: 1.3 }}>{children}</h1>,
        h2: ({ children }) => <h2 style={{ fontSize: "1.3rem", fontWeight: 400, color: "#e8e0d0", margin: "1.5rem 0 0.75rem", lineHeight: 1.3 }}>{children}</h2>,
        h3: ({ children }) => <h3 style={{ fontSize: "1.1rem", fontWeight: 400, color: "#d8d0c0", margin: "1.25rem 0 0.5rem" }}>{children}</h3>,
        p: ({ children }) => <p style={{ fontSize: "1rem", lineHeight: 1.85, color: "#c8c0b0", margin: "0 0 1.25rem" }}>{children}</p>,
        strong: ({ children }) => <strong style={{ color: "#e8e0d0", fontWeight: 600 }}>{children}</strong>,
        em: ({ children }) => <em style={{ color: "#b8b0a0", fontStyle: "italic" }}>{children}</em>,
        ul: ({ children }) => <ul style={{ color: "#c8c0b0", paddingLeft: "1.5rem", margin: "0 0 1.25rem", lineHeight: 1.85 }}>{children}</ul>,
        ol: ({ children }) => <ol style={{ color: "#c8c0b0", paddingLeft: "1.5rem", margin: "0 0 1.25rem", lineHeight: 1.85 }}>{children}</ol>,
        li: ({ children }) => <li style={{ marginBottom: "0.35rem" }}>{children}</li>,
        blockquote: ({ children }) => (
          <blockquote style={{
            borderLeft: "3px solid #3a3a3a",
            paddingLeft: "1.25rem",
            margin: "1.5rem 0",
            color: "#888",
            fontStyle: "italic",
          }}>{children}</blockquote>
        ),
        code: ({ children }) => (
          <code style={{
            background: "#1a1a1a",
            border: "1px solid #2a2a2a",
            borderRadius: "3px",
            padding: "0.1rem 0.4rem",
            fontSize: "0.85rem",
            fontFamily: "monospace",
            color: "#a8c8a8",
          }}>{children}</code>
        ),
        hr: () => <hr style={{ border: "none", borderTop: "1px solid #1e1e1e", margin: "2rem 0" }} />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
