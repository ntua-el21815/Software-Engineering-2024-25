from flask import Flask
from database.db_config import init_db
from routes.admin_routes import admin_routes
from routes.analysis_routes import analysis_routes
from routes.auth_routes import auth_routes
from models import TollOperator
from database.db_config import db
import os
import socket

app = Flask(__name__)

# Ρύθμιση βάσης δεδομένων
init_db(app)

# Καταχώρηση των routes
app.register_blueprint(admin_routes, url_prefix='/api/admin')
app.register_blueprint(analysis_routes, url_prefix='/api')
app.register_blueprint(auth_routes, url_prefix='/api')

# Συνάρτηση που εγγυάται πως θα υπάρχει ADMIN user στη βάση δεδομένων
def create_admin():
    admin_exists = db.session.query(TollOperator).filter_by(OpID='admin').first()
    if admin_exists is None:
        admin_user = TollOperator(
            OpID='ADMIN',
            Name='administrator',
            Email='admin@example.com',
            password='freepasses4all'  
        )
        db.session.add(admin_user)
        db.session.commit()

# Ρίζα για δοκιμή
@app.route('/')
def index():
    return "Welcome to the Softeng24 Toll Management API!"

if __name__ == '__main__':
    # Τοποθεσία του αρχείου της τρέχουσας εφαρμογής
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # Τοποθεσία του αρχείου του SSL certificate
    context = (this_dir + '/ssl/server.crt', this_dir + '/ssl/server.key')
    # Απόκτηση της ip του server
    ip = "0.0.0.0"
    app.run(host=ip, port=9115, ssl_context=context, debug=True)