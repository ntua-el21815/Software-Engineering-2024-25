from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

db = SQLAlchemy()

load_dotenv()
username = "root"
password = quote_plus(os.getenv("DB_PASSWORD_LOCAL"))
host = "127.0.0.1"
database = "toll management system"

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{username}:{password}@{host}:3306/{database}"
    #f"?ssl_ca={ssl_cert}&charset=utf8mb4"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,  # Recycle connections every 30 minutes
        "pool_timeout": 10,  # Wait 10 seconds before failing to get a connection
        "pool_size": 10,  # Maintain a small pool of reusable connections
        "max_overflow": 20,  # Allow up to 20 extra connections in demand
    }
    db.init_app(app)





