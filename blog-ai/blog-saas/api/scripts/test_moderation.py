#!/usr/bin/env python
"""
Script para probar la moderación de un post específico
Uso: python scripts/test_moderation.py <post_id>
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.post_moderation_adapter import PostModerationAdapter

def test_post(post_id):
    db = SessionLocal()
    adapter = PostModerationAdapter()
    try:
        print(f"🔍 Probando moderación del post {post_id}...")
        post = adapter.moderate_post(db, post_id)
        if post:
            print(f"✅ Post {post.id}:")
            print(f"   - Score: {post.policy_score}")
            print(f"   - Status: {post.status}")
            print(f"   - Razón: {post.policy_reason}")
            
            # Mostrar los primeros 200 caracteres del post
            print(f"\n📝 Primeros 200 caracteres:")
            print(post.body_md[:200] + "...")
        else:
            print(f"❌ Post {post_id} no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    post_id = int(sys.argv[1]) if len(sys.argv) > 1 else 142
    test_post(post_id)
