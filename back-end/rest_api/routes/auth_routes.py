from flask import Blueprint, request, jsonify
from models import TollOperator
import hashlib
import secrets

auth_routes = Blueprint('auth_routes', __name__)

# Temporary storage for tokens (In-memory)
tokens = {}

# Function to hash passwords (for demonstration purposes)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login endpoint
@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')

        # Validation of input
        if not username or not password:
            return jsonify({"status": "failed", "info": "Missing username or password"}), 400

        # Find user in database
        user = TollOperator.query.filter_by(OpID=username).first()
        if not user:
            return jsonify({"status": "failed", "info": "Invalid credentials"}), 401

        # Check if password matches

        if user.OpID == username and user.password == password:
            # Generate a secure token
            token = secrets.token_hex(16)
            tokens[token] = username  # Store token with associated username

            return jsonify({"token": token}), 200
        else:
            return jsonify({"status": "failed", "info": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

# Logout endpoint
@auth_routes.route('/logout', methods=['POST'])
def logout():
    try:
        # Get token from custom header
        token = request.headers.get("X-OBSERVATORY-AUTH")
        if not token:
            return jsonify({"status": "failed", "info": "Missing token"}), 400

        # Check if token exists
        if token in tokens:
            del tokens[token]  # Remove token from store
            return '', 200  # Empty response with status code 200
        else:
            return jsonify({"status": "failed", "info": "Invalid or expired token"}), 401
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

# Middleware to protect routes (optional)
def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get("X-OBSERVATORY-AUTH")
        if not token or token not in tokens:
            return jsonify({"status": "failed", "info": "Unauthorized"}), 401
        return f(*args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator