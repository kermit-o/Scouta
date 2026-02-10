from sqlalchemy.orm import relationship
try:
    # ajusta estos imports a tus modelos reales
    from backend.app.core.database.models import User, Subscription  # si tu módulo difiere, cámbialo
except Exception:
    # si los modelos viven en otro paquete del core:
    try:
        from backend.app.core.models import User, Subscription  # fallback
    except Exception:
        User = Subscription = None

def apply_relations_safe():
    try:
        if not (User and Subscription):
            return
        # evitar re-definir si ya existen
        if not hasattr(Subscription, "user_id"):
            # si no hay FK, no forcemos la relación dinámica
            return
        if not hasattr(User, "subscriptions"):
            User.subscriptions = relationship(
                "Subscription", back_populates="user",
                cascade="all, delete-orphan"
            )
        if not hasattr(Subscription, "user"):
            Subscription.user = relationship(
                "User", back_populates="subscriptions"
            )
        print("✅ Relación de suscripción agregada al modelo User")
    except Exception as e:
        print("⚠️  Error configurando relaciones:", e)
