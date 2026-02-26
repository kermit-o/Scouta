#!/usr/bin/env python
"""
CLI para moderar posts directamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.post_moderation_adapter import PostModerationAdapter

def moderate_posts(limit=10, post_id=None):
    db = SessionLocal()
    adapter = PostModerationAdapter()
    
    try:
        if post_id:
            # Moderar un post específico
            print(f"🔍 Moderando post {post_id}...")
            post = adapter.moderate_post(db, post_id)
            if post:
                print(f"✅ Post {post.id}: score={post.policy_score}, status={post.status}")
                print(f"📝 Razón: {post.policy_reason}")
            else:
                print(f"❌ Post {post_id} no encontrado")
        else:
            # Moderar lote
            posts = db.query(Post).filter(
                Post.status == "needs_review",
                Post.policy_score.is_(None)
            ).limit(limit).all()
            
            print(f"📊 Moderando {len(posts)} posts...")
            for post in posts:
                moderated = adapter.moderate_post(db, post.id)
                if moderated:
                    print(f"  ✅ Post {moderated.id}: score={moderated.policy_score}, status={moderated.status}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", type=int, help="ID del post específico")
    parser.add_argument("--limit", type=int, default=10, help="Límite de posts")
    args = parser.parse_args()
    
    moderate_posts(limit=args.limit, post_id=args.post_id)
