from flask import Flask
from database.db_config import init_db
from routes.admin_routes import admin_routes
from routes.pass_routes import pass_routes
from routes.analysis_routes import analysis_routes
from routes.auth_routes import auth_routes

app = Flask(__name__)

# Ρύθμιση βάσης δεδομένων
init_db(app)

# Καταχώρηση των routes
app.register_blueprint(admin_routes, url_prefix='/api/admin')
app.register_blueprint(pass_routes, url_prefix='/api')
app.register_blueprint(analysis_routes, url_prefix='/api')
app.register_blueprint(auth_routes, url_prefix='/api')

# Ρίζα για δοκιμή
@app.route('/')
def index():
    return "Welcome to the Softeng24 Toll Management API!"

if __name__ == '__main__':
    app.run(debug=True, port=9115)