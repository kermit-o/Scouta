import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://serene-eagerness-production.up.railway.app")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")

def send_verification_email(to_email: str, username: str, token: str) -> bool:
    try:
        verify_url = f"{FRONTEND_URL}/verify-email?token={token}"
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Verify your Scouta account",
            "html": f"""
            <div style="font-family: monospace; max-width: 500px; margin: 0 auto; padding: 2rem; background: #0a0a0a; color: #e0e0e0;">
                <h1 style="font-size: 1.5rem; color: #fff;">Welcome to Scouta, {username}</h1>
                <p style="color: #888;">Click below to verify your email and join the debate.</p>
                <a href="{verify_url}" 
                   style="display: inline-block; margin: 1.5rem 0; padding: 0.75rem 1.5rem; background: #fff; color: #000; text-decoration: none; font-weight: bold;">
                    Verify Email
                </a>
                <p style="color: #444; font-size: 0.8rem;">Or copy this link: {verify_url}</p>
                <p style="color: #444; font-size: 0.8rem;">This link expires in 24 hours.</p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"[email] error: {e}")
        return False
