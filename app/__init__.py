from flask import Flask

from .extensions import db, login_manager
from .models import User


def create_app() -> Flask:
    
    app = Flask(__name__)

    
    app.config["SECRET_KEY"] = "change-this-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    
    from app.routes import main
    app.register_blueprint(main)

    return app
