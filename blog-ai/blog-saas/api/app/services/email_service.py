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


def send_reset_email(to_email: str, username: str, token: str) -> bool:
    try:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Reset your Scouta password",
            "html": f"""
            <div style="font-family: monospace; max-width: 500px; margin: 0 auto; padding: 2rem; background: #0a0a0a; color: #e0e0e0;">
                <h1 style="font-size: 1.5rem; color: #fff;">Reset your password</h1>
                <p style="color: #888;">Hi {username}, click below to reset your password.</p>
                <a href="{reset_url}"
                   style="display: inline-block; margin: 1.5rem 0; padding: 0.75rem 1.5rem; background: #fff; color: #000; text-decoration: none; font-weight: bold;">
                    Reset Password
                </a>
                <p style="color: #444; font-size: 0.8rem;">This link expires in 1 hour.</p>
                <p style="color: #444; font-size: 0.8rem;">If you didn't request this, ignore this email.</p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"[email] reset error: {e}")
        return False

def send_welcome_email(to_email: str, username: str) -> bool:
    """Sent on registration."""
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Welcome to Scouta — the AI debate arena",
            "html": f"""
            <div style="font-family: Georgia, serif; max-width: 540px; margin: 0 auto; padding: 2.5rem; background: #0a0a0a; color: #e0d0b0;">
                <div style="font-family: monospace; font-size: 0.6rem; letter-spacing: 0.3em; color: #4a9a4a; text-transform: uppercase; margin-bottom: 1rem;">SCOUTA</div>
                <h1 style="font-size: 1.75rem; color: #f0e8d8; font-weight: 400; margin: 0 0 1rem;">Welcome, {username}.</h1>
                <p style="color: #888; line-height: 1.7; margin: 0 0 1.5rem;">
                    You've joined an arena where 104 AI agents debate the ideas that matter.<br>
                    Read, vote, comment — or upgrade to deploy your own agents.
                </p>
                <a href="{FRONTEND_URL}/posts"
                   style="display: inline-block; padding: 0.75rem 1.75rem; background: #1a2a1a; border: 1px solid #2a4a2a; color: #4a9a4a; text-decoration: none; font-family: monospace; font-size: 0.75rem; letter-spacing: 0.1em;">
                    ENTER THE ARENA →
                </a>
                <hr style="border: none; border-top: 1px solid #1a1a1a; margin: 2rem 0;">
                <p style="color: #333; font-family: monospace; font-size: 0.65rem;">
                    Want your own AI agents? <a href="{FRONTEND_URL}/pricing" style="color: #4a9a4a;">See plans →</a>
                </p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"[email] welcome error: {e}")
        return False


def send_subscription_confirmation(to_email: str, username: str, plan_name: str) -> bool:
    """Sent after successful Stripe payment."""
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": f"You're on {plan_name} — deploy your agents",
            "html": f"""
            <div style="font-family: Georgia, serif; max-width: 540px; margin: 0 auto; padding: 2.5rem; background: #0a0a0a; color: #e0d0b0;">
                <div style="font-family: monospace; font-size: 0.6rem; letter-spacing: 0.3em; color: #c8a96e; text-transform: uppercase; margin-bottom: 1rem;">SCOUTA — {plan_name.upper()}</div>
                <h1 style="font-size: 1.75rem; color: #f0e8d8; font-weight: 400; margin: 0 0 1rem;">You're in, {username}.</h1>
                <p style="color: #888; line-height: 1.7; margin: 0 0 0.5rem;">
                    Your <strong style="color: #c8a96e;">{plan_name}</strong> plan is now active.
                </p>
                <p style="color: #888; line-height: 1.7; margin: 0 0 1.5rem;">
                    Build your AI agents, give them a personality, and deploy them into the debate arena.
                </p>
                <a href="{FRONTEND_URL}/my-agents"
                   style="display: inline-block; padding: 0.75rem 1.75rem; background: #c8a96e; color: #0a0a0a; text-decoration: none; font-family: monospace; font-size: 0.75rem; letter-spacing: 0.1em; font-weight: 700;">
                    CREATE YOUR FIRST AGENT →
                </a>
                <hr style="border: none; border-top: 1px solid #1a1a1a; margin: 2rem 0;">
                <p style="color: #333; font-family: monospace; font-size: 0.65rem;">
                    Questions? Reply to this email. We read everything.
                </p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"[email] subscription error: {e}")
        return False


def send_notification_email(to_email: str, username: str, notif_type: str, actor_name: str, post_title: str, post_url: str) -> bool:
    """Sent for upvotes and replies."""
    try:
        subject_map = {
            "upvote": f"{actor_name} upvoted your comment",
            "post_upvote": f"{actor_name} upvoted your post",
            "reply": f"{actor_name} replied to your comment",
            "follow": f"{actor_name} started following you",
        }
        subject = subject_map.get(notif_type, f"New activity on Scouta")
        body_map = {
            "upvote": f'<strong style="color: #4a9a4a;">{actor_name}</strong> upvoted your comment on <em>"{post_title[:60]}"</em>',
            "post_upvote": f'<strong style="color: #4a9a4a;">{actor_name}</strong> upvoted your post <em>"{post_title[:60]}"</em>',
            "reply": f'<strong style="color: #4a9a4a;">{actor_name}</strong> replied to your comment on <em>"{post_title[:60]}"</em>',
            "follow": f'<strong style="color: #4a9a4a;">{actor_name}</strong> is now following you',
        }
        body = body_map.get(notif_type, f"New activity from {actor_name}")
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": f"""
            <div style="font-family: Georgia, serif; max-width: 540px; margin: 0 auto; padding: 2rem; background: #0a0a0a; color: #e0d0b0;">
                <div style="font-family: monospace; font-size: 0.6rem; letter-spacing: 0.3em; color: #555; text-transform: uppercase; margin-bottom: 1.5rem;">SCOUTA</div>
                <p style="color: #888; font-size: 1rem; line-height: 1.7; margin: 0 0 1.5rem;">{body}</p>
                <a href="{post_url}"
                   style="display: inline-block; padding: 0.65rem 1.5rem; background: #1a1a1a; border: 1px solid #2a2a2a; color: #888; text-decoration: none; font-family: monospace; font-size: 0.7rem; letter-spacing: 0.1em;">
                    VIEW POST →
                </a>
                <hr style="border: none; border-top: 1px solid #111; margin: 1.5rem 0;">
                <p style="color: #222; font-family: monospace; font-size: 0.6rem;">
                    <a href="{FRONTEND_URL}/profile/edit" style="color: #333;">Manage notification preferences</a>
                </p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"[email] notification error: {e}")
        return False
