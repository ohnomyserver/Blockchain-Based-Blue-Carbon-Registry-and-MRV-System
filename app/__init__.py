from flask import Flask
from dotenv import load_dotenv
import os

from .extensions import db, login_manager, bcrypt
from .models import User

load_dotenv()

def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    from app.routes import main
    from app.auth import auth
    from app.routes.credits import credits_bp

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(credits_bp)

    return app