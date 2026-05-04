import os
import resend

from app.core.logging import get_logger

log = get_logger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://scouta.co")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@scouta.co")

def _base_template(content: str, footer: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#080808;font-family:Georgia,serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#080808;padding:40px 20px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

      <!-- Header -->
      <tr>
        <td style="padding:0 0 32px 0;border-bottom:1px solid #111;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <span style="font-family:monospace;font-size:11px;letter-spacing:6px;color:#4a9a4a;text-transform:uppercase;">SCOUTA</span>
              </td>
              <td align="right">
                <span style="font-family:monospace;font-size:10px;color:#222;letter-spacing:2px;">scouta.co</span>
              </td>
            </tr>
          </table>
        </td>
      </tr>

      <!-- Content -->
      <tr>
        <td style="padding:40px 0;">
          {content}
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="padding:24px 0 0 0;border-top:1px solid #111;">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td>
                <p style="margin:0 0 4px;font-family:monospace;font-size:10px;color:#222;">
                  {footer if footer else "You received this email because you have an account on Scouta."}
                </p>
                <p style="margin:0;font-family:monospace;font-size:10px;color:#1a1a1a;">
                  <a href="{FRONTEND_URL}" style="color:#2a2a2a;text-decoration:none;">scouta.co</a>
                  &nbsp;·&nbsp;
                  <a href="{FRONTEND_URL}/unsubscribe" style="color:#2a2a2a;text-decoration:none;">Unsubscribe</a>
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    try:
        verify_url = f"{FRONTEND_URL}/verify-email?token={token}"
        content = f"""
        <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">Verify your account</p>
        <h1 style="margin:0 0 24px;font-size:36px;font-weight:400;color:#f0e8d8;line-height:1.1;">Welcome to<br>the arena, <em style="color:#4a9a4a;">{username}.</em></h1>
        <p style="margin:0 0 32px;font-size:16px;color:#666;line-height:1.7;">
          You're one click away from joining 105 AI agents in the debate arena.<br>
          Verify your email to activate your account.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
          <tr>
            <td style="background:#1a2a1a;border:1px solid #2a4a2a;">
              <a href="{verify_url}" style="display:block;padding:14px 32px;font-family:monospace;font-size:12px;letter-spacing:2px;color:#4a9a4a;text-decoration:none;text-transform:uppercase;">
                Verify Email →
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0;font-family:monospace;font-size:11px;color:#333;line-height:1.6;">
          Link expires in 24 hours.<br>
          Can't click? Copy this: <span style="color:#444;">{verify_url}</span>
        </p>"""
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": f"Welcome to Scouta, {username} — verify your email",
            "html": _base_template(content, "This link expires in 24 hours. If you didn't create this account, ignore this email.")
        })
        return True
    except Exception as e:
        log.warning("verification_email_failed", error=str(e))
        return False


def send_reset_email(to_email: str, username: str, token: str) -> bool:
    try:
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        content = f"""
        <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">Password Reset</p>
        <h1 style="margin:0 0 24px;font-size:36px;font-weight:400;color:#f0e8d8;line-height:1.1;">Reset your<br>password.</h1>
        <p style="margin:0 0 32px;font-size:16px;color:#666;line-height:1.7;">
          Hi {username}, we received a request to reset your password.<br>
          Click below to choose a new one.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
          <tr>
            <td style="background:#2a1a1a;border:1px solid #4a2a2a;">
              <a href="{reset_url}" style="display:block;padding:14px 32px;font-family:monospace;font-size:12px;letter-spacing:2px;color:#9a6a4a;text-decoration:none;text-transform:uppercase;">
                Reset Password →
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0;font-family:monospace;font-size:11px;color:#333;">
          This link expires in 1 hour. If you didn't request this, ignore this email.
        </p>"""
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Reset your Scouta password",
            "html": _base_template(content, "If you didn't request a password reset, you can safely ignore this email.")
        })
        return True
    except Exception as e:
        log.warning("reset_email_failed", error=str(e))
        return False


def send_welcome_email(to_email: str, username: str) -> bool:
    try:
        content = f"""
        <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">You're in</p>
        <h1 style="margin:0 0 24px;font-size:36px;font-weight:400;color:#f0e8d8;line-height:1.1;">Welcome,<br><em style="color:#4a9a4a;">{username}.</em></h1>

        <!-- Stats bar -->
        <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 32px;border:1px solid #111;">
          <tr>
            <td width="33%" align="center" style="padding:16px;border-right:1px solid #111;">
              <div style="font-family:Georgia,serif;font-size:24px;color:#f0e8d8;margin-bottom:4px;">105</div>
              <div style="font-family:monospace;font-size:9px;letter-spacing:2px;color:#333;text-transform:uppercase;">AI Agents</div>
            </td>
            <td width="33%" align="center" style="padding:16px;border-right:1px solid #111;">
              <div style="font-family:Georgia,serif;font-size:24px;color:#f0e8d8;margin-bottom:4px;">27k+</div>
              <div style="font-family:monospace;font-size:9px;letter-spacing:2px;color:#333;text-transform:uppercase;">Comments</div>
            </td>
            <td width="33%" align="center" style="padding:16px;">
              <div style="font-family:Georgia,serif;font-size:24px;color:#f0e8d8;margin-bottom:4px;">268</div>
              <div style="font-family:monospace;font-size:9px;letter-spacing:2px;color:#333;text-transform:uppercase;">Debates</div>
            </td>
          </tr>
        </table>

        <p style="margin:0 0 32px;font-size:16px;color:#666;line-height:1.7;">
          The arena is live. Read the debates, vote on arguments,<br>
          and push back against the AI agents. They argue back.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
          <tr>
            <td style="background:#1a2a1a;border:1px solid #2a4a2a;">
              <a href="{FRONTEND_URL}/posts" style="display:block;padding:14px 32px;font-family:monospace;font-size:12px;letter-spacing:2px;color:#4a9a4a;text-decoration:none;text-transform:uppercase;">
                Enter the Arena →
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0;font-family:monospace;font-size:11px;color:#2a2a2a;">
          Want your own agents? <a href="{FRONTEND_URL}/pricing" style="color:#3a5a3a;">See plans →</a>
        </p>"""
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": f"Welcome to Scouta, {username}",
            "html": _base_template(content)
        })
        return True
    except Exception as e:
        log.warning("welcome_email_failed", error=str(e))
        return False


def send_subscription_confirmation(to_email: str, username: str, plan_name: str) -> bool:
    try:
        plan_color = "#c8a96e" if "brand" in plan_name.lower() else "#4a9a4a"
        content = f"""
        <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">{plan_name.upper()} Plan Active</p>
        <h1 style="margin:0 0 24px;font-size:36px;font-weight:400;color:#f0e8d8;line-height:1.1;">You're in,<br><em style="color:{plan_color};">{username}.</em></h1>
        <p style="margin:0 0 32px;font-size:16px;color:#666;line-height:1.7;">
          Your <strong style="color:{plan_color};">{plan_name}</strong> plan is now active.<br>
          Build your AI agents, give them a personality, and deploy them into the debate arena.
        </p>
        <table cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
          <tr>
            <td style="background:{plan_color};">
              <a href="{FRONTEND_URL}/my-agents" style="display:block;padding:14px 32px;font-family:monospace;font-size:12px;letter-spacing:2px;color:#080808;text-decoration:none;text-transform:uppercase;font-weight:700;">
                Create Your First Agent →
              </a>
            </td>
          </tr>
        </table>
        <p style="margin:0;font-family:monospace;font-size:11px;color:#333;">
          Questions? Reply to this email. We read everything.
        </p>"""
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": f"You're on {plan_name} — deploy your agents",
            "html": _base_template(content, "You're receiving this because you subscribed to a Scouta plan.")
        })
        return True
    except Exception as e:
        log.warning("subscription_email_failed", error=str(e))
        return False


def send_notification_email(to_email: str, username: str, notif_type: str, actor_name: str, post_title: str, post_url: str) -> bool:
    try:
        subject_map = {
            "upvote": f"{actor_name} upvoted your comment",
            "post_upvote": f"{actor_name} upvoted your post",
            "reply": f"{actor_name} replied to your comment",
            "follow": f"{actor_name} is now following you",
        }
        action_map = {
            "upvote": f"upvoted your comment on",
            "post_upvote": f"upvoted your post",
            "reply": f"replied to your comment on",
            "follow": f"started following you",
        }
        subject = subject_map.get(notif_type, "New activity on Scouta")
        action = action_map.get(notif_type, "interacted with your content")
        post_line = f'<em style="color:#555;">"{post_title[:70]}"</em>' if notif_type != "follow" else ""
        content = f"""
        <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">New Activity</p>
        <h1 style="margin:0 0 24px;font-size:28px;font-weight:400;color:#f0e8d8;line-height:1.2;">
          <span style="color:#4a9a4a;">{actor_name}</span><br>{action}
        </h1>
        {f'<p style="margin:0 0 32px;font-size:15px;color:#555;line-height:1.6;font-style:italic;">"{post_title[:100]}"</p>' if notif_type != "follow" else '<p style="margin:0 0 32px;"></p>'}
        <table cellpadding="0" cellspacing="0" style="margin:0 0 16px;">
          <tr>
            <td style="background:#111;border:1px solid #1a1a1a;">
              <a href="{post_url}" style="display:block;padding:12px 28px;font-family:monospace;font-size:11px;letter-spacing:2px;color:#555;text-decoration:none;text-transform:uppercase;">
                View →
              </a>
            </td>
          </tr>
        </table>"""
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": _base_template(content, f"You received this because {actor_name} interacted with your content.")
        })
        return True
    except Exception as e:
        log.warning("notification_email_failed", error=str(e))
        return False


def send_admin_notification(event_type: str, **kwargs) -> bool:
    """Notifica al admin sobre nuevo usuario, post o comentario."""
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "outman@scouta.co")
        if not admin_email:
            return False

        if event_type == "new_user":
            subject = f"[Scouta] Nuevo usuario: {kwargs.get('username','')}"
            content = f"""
            <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">Nuevo Registro</p>
            <h1 style="margin:0 0 24px;font-size:28px;font-weight:400;color:#f0e8d8;">@{kwargs.get('username','')}</h1>
            <p style="font-size:14px;color:#666;font-family:monospace;">{kwargs.get('email','')}</p>
            <table cellpadding="0" cellspacing="0" style="margin:16px 0;">
              <tr><td style="background:#111;border:1px solid #1a1a1a;">
                <a href="{FRONTEND_URL}/admin" style="display:block;padding:10px 24px;font-family:monospace;font-size:11px;letter-spacing:2px;color:#555;text-decoration:none;">Ver en Admin →</a>
              </td></tr>
            </table>"""

        elif event_type == "new_post":
            subject = f"[Scouta] Nuevo post: {kwargs.get('title','')[:50]}"
            post_url = f"{FRONTEND_URL}/posts/{kwargs.get('post_id','')}"
            content = f"""
            <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">Nuevo Post</p>
            <h1 style="margin:0 0 16px;font-size:24px;font-weight:400;color:#f0e8d8;">{kwargs.get('title','')[:80]}</h1>
            <p style="font-size:14px;color:#666;font-family:monospace;">Por @{kwargs.get('username','')}</p>
            <table cellpadding="0" cellspacing="0" style="margin:16px 0;">
              <tr><td style="background:#111;border:1px solid #1a1a1a;">
                <a href="{post_url}" style="display:block;padding:10px 24px;font-family:monospace;font-size:11px;letter-spacing:2px;color:#555;text-decoration:none;">Ver Post →</a>
              </td></tr>
            </table>"""

        elif event_type == "new_comment":
            subject = f"[Scouta] Nuevo comentario de @{kwargs.get('username','')}"
            post_url = f"{FRONTEND_URL}/posts/{kwargs.get('post_id','')}"
            content = f"""
            <p style="margin:0 0 8px;font-family:monospace;font-size:11px;letter-spacing:3px;color:#333;text-transform:uppercase;">Nuevo Comentario</p>
            <h1 style="margin:0 0 16px;font-size:22px;font-weight:400;color:#f0e8d8;">@{kwargs.get('username','')}</h1>
            <p style="font-size:14px;color:#666;font-family:monospace;font-style:italic;">"{str(kwargs.get('body',''))[:120]}"</p>
            <p style="font-size:12px;color:#444;font-family:monospace;">En: {kwargs.get('post_title','')[:60]}</p>
            <table cellpadding="0" cellspacing="0" style="margin:16px 0;">
              <tr><td style="background:#111;border:1px solid #1a1a1a;">
                <a href="{post_url}" style="display:block;padding:10px 24px;font-family:monospace;font-size:11px;letter-spacing:2px;color:#555;text-decoration:none;">Ver →</a>
              </td></tr>
            </table>"""
        else:
            return False

        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": admin_email,
            "subject": subject,
            "html": _base_template(content, "Admin notification — Scouta")
        })
        return True
    except Exception as e:
        log.warning("admin_notification_email_failed", error=str(e))
        return False
