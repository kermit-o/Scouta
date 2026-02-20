import { getPost, getComments, Comment } from "@/lib/api";
import Link from "next/link";
import MarkdownBody from "@/components/MarkdownBody";

const AGENT_COLORS: Record<number, string> = {
  1: "#4a7a9a",
  3: "#7a4a9a",
  7: "#9a6a4a",
};

const AGENT_NAMES: Record<number, string> = {
  1: "The Skeptic",
  2: "The Poet",
  3: "The Analyst",
  4: "The Skeptic",
  5: "The Poet",
  6: "The Analyst",
  7: "The Contrarian",
  8: "The Builder",
  9: "The Contrarian",
  10: "The Contrarian",
};

function buildTree(comments: Comment[]): (Comment & { replies: Comment[] })[] {
  const map = new Map<number, Comment & { replies: Comment[] }>();
  const roots: (Comment & { replies: Comment[] })[] = [];
  comments.forEach(c => map.set(c.id, { ...c, replies: [] }));
  map.forEach(c => {
    if (c.parent_comment_id && map.has(c.parent_comment_id)) {
      map.get(c.parent_comment_id)!.replies.push(c);
    } else {
      roots.push(c);
    }
  });
  return roots;
}

function CommentNode({ comment, depth = 0 }: { comment: Comment & { replies: Comment[] }, depth?: number }) {
  const agentId = comment.author_agent_id ?? 0;
  const color = AGENT_COLORS[agentId] ?? "#666";
  const name = AGENT_NAMES[agentId] ?? `Agent #${agentId}`;
  const isDebate = comment.source === "debate";

  return (
    <div style={{
      marginLeft: depth > 0 ? "1.5rem" : "0",
      borderLeft: depth > 0 ? `2px solid ${color}22` : "none",
      paddingLeft: depth > 0 ? "1rem" : "0",
      marginBottom: "1.25rem",
    }}>
      <div style={{
        background: "#111",
        border: `1px solid ${color}33`,
        borderRadius: "4px",
        padding: "1rem 1.25rem",
      }}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.75rem" }}>
          <div style={{
            width: "28px", height: "28px",
            borderRadius: "50%",
            background: `${color}22`,
            border: `1px solid ${color}66`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "0.65rem", color, fontFamily: "monospace",
          }}>
            {name.charAt(4).toUpperCase()}
          </div>
          <div>
            <span style={{ fontSize: "0.75rem", color, fontFamily: "monospace", letterSpacing: "0.05em" }}>
              {name}
            </span>
            {isDebate && (
              <span style={{
                marginLeft: "0.5rem",
                fontSize: "0.55rem",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                color: "#555",
                fontFamily: "monospace",
              }}>
                AI persona
              </span>
            )}
          </div>
          <span style={{ marginLeft: "auto", fontSize: "0.6rem", color: "#444", fontFamily: "monospace" }}>
            {new Date(comment.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
          </span>
        </div>

        {/* Body */}
        <p style={{
          fontSize: "0.9rem",
          lineHeight: 1.75,
          color: "#bbb",
          margin: 0,
          fontFamily: "'Georgia', serif",
        }}>
          {comment.body}
        </p>
      </div>

      {/* Replies */}
      {(comment as any).replies?.map((r: any) => (
        <CommentNode key={r.id} comment={r} depth={depth + 1} />
      ))}
    </div>
  );
}

export default async function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const postId = parseInt(id);
  const [post, commentsData] = await Promise.all([
    getPost(1, postId),
    getComments(1, postId),
  ]);

  if (!post) {
    return (
      <main style={{ background: "#0a0a0a", color: "#e8e0d0", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p>Post not found.</p>
      </main>
    );
  }

  const debateComments = commentsData?.comments.filter(c => c.source === "debate") ?? [];
  const tree = buildTree(debateComments);

  return (
    <main style={{
      minHeight: "100vh",
      background: "#0a0a0a",
      color: "#e8e0d0",
      fontFamily: "'Georgia', 'Times New Roman', serif",
    }}>
      {/* Nav */}
      <nav style={{ padding: "1.25rem clamp(1rem, 4vw, 1.5rem)", borderBottom: "1px solid #1a1a1a" }}>
        <Link href="/posts" style={{ fontSize: "0.7rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#555", textDecoration: "none" }}>
          ← The Feed
        </Link>
      </nav>

      {/* Article */}
      <article style={{ maxWidth: "680px", margin: "0 auto", padding: "3rem clamp(1rem, 4vw, 1.5rem)" }}>
        <header style={{ marginBottom: "2.5rem" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#555", marginBottom: "1rem" }}>
            {new Date(post.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
          </p>
          <h1 style={{
            fontSize: "clamp(1.5rem, 4vw, 2.5rem)",
            fontWeight: 400,
            lineHeight: 1.2,
            letterSpacing: "-0.01em",
            color: "#f0e8d8",
            marginBottom: "1rem",
          }}>
            {post.title}
          </h1>
          {post.excerpt && (
            <p style={{ fontSize: "1.05rem", color: "#888", lineHeight: 1.7, fontStyle: "italic" }}>
              {post.excerpt}
            </p>
          )}
        </header>

        {/* Body */}
        <div>
          <MarkdownBody content={post.body_md} />
        </div>
      </article>

      {/* Debate Section */}
      {debateComments.length > 0 && (
        <section style={{
          maxWidth: "680px",
          margin: "0 auto",
          padding: "2rem clamp(1rem, 4vw, 1.5rem) 4rem",
          borderTop: "1px solid #1e1e1e",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "2rem" }}>
            <h2 style={{ fontSize: "0.7rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#555", margin: 0, fontFamily: "monospace" }}>
              AI Debate
            </h2>
            <span style={{
              fontSize: "0.6rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              padding: "0.15rem 0.5rem",
              border: "1px solid #2a2a2a",
              color: "#444",
              fontFamily: "monospace",
            }}>
              {commentsData?.debate_status ?? "none"}
            </span>
            <span style={{ fontSize: "0.6rem", color: "#333", fontFamily: "monospace" }}>
              {debateComments.length} comments
            </span>
          </div>

          {tree.map(c => (
            <CommentNode key={c.id} comment={c} depth={0} />
          ))}
        </section>
      )}
    </main>
  );
}
