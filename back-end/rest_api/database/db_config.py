from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://se2427admin:y%A4J#zA;2%]}hY@se24-27db.mysql.database.azure.com:3306/new_database?ssl_ca=/Users/Aggeliki/Desktop/Τεχνολογία Λογισμικού/Πρότζεκτ/DigiCertGlobalRootCA.crt.pem'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)