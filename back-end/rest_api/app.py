from flask import Flask
from database.db_config import init_db
from routes.admin_routes import admin_routes
from routes.analysis_routes import analysis_routes
from routes.auth_routes import auth_routes
import os

app = Flask(__name__)

init_db(app)

app.register_blueprint(admin_routes, url_prefix='/api/admin')
app.register_blueprint(analysis_routes, url_prefix='/api')
app.register_blueprint(auth_routes, url_prefix='/api')

@app.route('/')
def index():
    return "Welcome to the Softeng24 Toll Management API!"

if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.abspath(__file__))
    context = (this_dir + '/ssl/server.crt', this_dir + '/ssl/server.key')
    app.run(debug=True,host="127.0.0.1", port=9115, ssl_context=context)