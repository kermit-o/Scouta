# backend/services/notifications.py
async def send_confirmation_email(email: str, reservation_id: str):
    """Enviar email de confirmación"""
    # Implementación simulada
    print(f"📧 Email enviado a {email} para reserva {reservation_id}")
    return True