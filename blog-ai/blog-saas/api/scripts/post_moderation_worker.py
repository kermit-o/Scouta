#!/usr/bin/env python
"""
Worker de moderación - Usa PostModerationAdapter
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.post_moderation_adapter import PostModerationAdapter

def run_cycle():
    db = SessionLocal()
    adapter = PostModerationAdapter()
    
    try:
        # Obtener posts sin score
        posts = db.query(Post).filter(
            Post.status == "needs_review",
            Post.policy_score.is_(None)
        ).limit(10).all()
        
        print(f"📊 Moderando {len(posts)} posts...")
        
        for post in posts:
            moderated = adapter.moderate_post(db, post.id)
            if moderated:
                status = "✅ publicado" if moderated.status == "published" else "⏳ needs_review"
                print(f"  {status} - Post {moderated.id} (score: {moderated.policy_score})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Worker de moderación iniciado")
    cycles = 0
    while True:
        try:
            cycles += 1
            print(f"\n🔄 Ciclo #{cycles} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            run_cycle()
            print(f"⏱️  Esperando 5 minutos...")
            time.sleep(300)  # 5 minutos
        except KeyboardInterrupt:
            print("\n👋 Worker detenido")
            break
        except Exception as e:
            print(f"❌ Error en ciclo: {e}")
            time.sleep(60)
