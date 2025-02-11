from flask import Blueprint, request, jsonify
from models import TollOperator, db
import bcrypt
import secrets
from functools import wraps


auth_routes = Blueprint('auth_routes', __name__)

tokens = {}

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

@auth_routes.route('/login', methods=['POST'])
def login():
    """Επιστρέφει ένα token αν τα διαπιστευτήρια είναι σωστά."""
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"status": "failed", "info": "Missing username or password"}), 400

        user = TollOperator.query.filter_by(OpID=username).first()

        if user:
            stored_password = user.password

            # Αν ο κωδικός στη βάση δεν είναι bcrypt hash, τον αναβαθμίζουμε
            if not stored_password.startswith("$2b$"):
                new_hashed_password = bcrypt.hashpw(stored_password.encode(), bcrypt.gensalt()).decode()
                user.password = new_hashed_password
                db.session.commit()  # Αποθήκευση του νέου hash στη βάση

            # Επαλήθευση του bcrypt password
            if bcrypt.checkpw(password.encode(), user.password.encode()):
                token = secrets.token_hex(16)
                tokens[token] = username
                return jsonify({"token": token}), 200

        return jsonify({"status": "failed", "info": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

@auth_routes.route('/logout', methods=['POST'])
def logout():
    """Διαγράφει το token του χρήστη αν υπάρχει στο request header."""
    try:
        token = request.headers.get("X-OBSERVATORY-AUTH")
        if not token:
            return jsonify({"status": "failed", "info": "Missing token"}), 400

        if token in tokens:
            del tokens[token] 
            return '', 200 
        else:
            return jsonify({"status": "failed", "info": "Invalid or expired token"}), 401
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500
    
def token_required(f):
    """Decorator που απαιτεί να είναι ο χρήστης συνδεδεμένος (με valid token)."""
    def decorated_function(*args, **kwargs):
        token = request.headers.get("X-OBSERVATORY-AUTH")
        if not token or token not in tokens:
            return jsonify({"status": "failed", "info": "Unauthorized"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function