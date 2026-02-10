import os
from flask import Flask
from dotenv import load_dotenv

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("WEB_SECRET_KEY", "dev-secret-change-me")
    app.config["API_BASE_URL"] = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

    from app.routes.public import bp as public_bp
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    @app.get("/health")
    def health():
        return {"ok": True, "service": "web"}

    return app
