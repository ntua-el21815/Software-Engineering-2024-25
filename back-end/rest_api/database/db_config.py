from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

db = SQLAlchemy()

username = "se2427admin"
password = quote_plus("y%A4J#zA;2%]}hY")
host = "se24-27db.mysql.database.azure.com"
database = "toll management system"
ssl_cert = "/Users/Aggeliki/Desktop/Τεχνολογία Λογισμικού/Πρότζεκτ/DigiCertGlobalRootCA.crt.pem"

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{username}:{password}@{host}:3306/{database}"
    f"?ssl_ca={ssl_cert}&charset=utf8mb4"
)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)





