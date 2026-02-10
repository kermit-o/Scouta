import os
from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    @app.get(/health)
    def health(): return jsonify(status=ok)
    return app

if __name__ == __main__:
    app = create_app()
    app.run(host=0.0.0.0, port=int(os.getenv(PORT, 5000)))
