from flask import Flask
from flask_cors import CORS # To handle Cross-Origin Resource Sharing
import os

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    # app.config.from_object(config.get(config_name or 'default')) # Example for config files
    # app.config.from_pyfile('config.py', silent=True) # Example for instance config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "a_very_secret_key_for_development")
    # Database configuration (example for SQLite)
    # app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or \
    #     f"sqlite:///{os.path.join(app.instance_path, 'app.sqlite')}"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions (e.g., SQLAlchemy, Migrate) here
    # from .models import db
    # db.init_app(app)
    # from flask_migrate import Migrate
    # migrate = Migrate(app, db)

    # Enable CORS for all domains on all routes. For production, configure it more strictly.
    CORS(app) 

    # Register Blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Add a simple test route
    @app.route("/hello")
    def hello():
        return "Hello from Flask Backend!"

    return app

