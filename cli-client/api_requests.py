import requests
import os
import urllib3
import warnings
import socket

# Suppress only the InsecureRequestWarning from urllib3
warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

ip = socket.gethostbyname(socket.gethostname())
BASE_URL = f"https://{ip}:9115/api"
TOKEN_FILE = "auth_token.txt"
ADMIN_ACCESS_FILE = "admin_access.txt"

def api_call(endpoint, method="GET", params=None, data=None, files=None, auth_required=False):
    url = f"{BASE_URL}/{endpoint}"
    headers = {}

    if auth_required:
        token = load_token()
        if token:
            headers["X-OBSERVATORY-AUTH"] = token
        else:
            print("No authentication token found. Please login first.")
            return None

    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, verify=False)
        elif method == "POST":
            response = requests.post(url, data=data, files=files, headers=headers, verify=False)
        else:
            raise ValueError("Unsupported HTTP method")

        if response.status_code == 401:
            print("Unauthorized request. Please login again.")
            delete_token()
            return None

        if response.status_code == 404:
            print(f"Error: API endpoint `{endpoint}` not found.")
            return None

        if response.status_code == 204 or (response.status_code == 200 and not response.text.strip()):
            return True  # Αντί για None, επιστρέφουμε επιτυχία

        # Αν το format είναι CSV, επιστρέφουμε το raw text
        if params and params.get("format") == "csv":
            return response.text  # To API επιστρέφει απευθείας CSV

        return response.json()  # Default: JSON format

    except requests.exceptions.ConnectionError:
        print("Failed to connect to API. Is the server running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def upload_passes_csv(file_path):
    """Στέλνει αρχείο CSV στο API για εισαγωγή διελεύσεων."""
    with open(file_path, "rb") as file:
        files = {"file": (file_path, file, "text/csv")}
        return api_call("admin/addpasses", method="POST", files=files)

def save_token(token):
    """Αποθηκεύει το authentication token σε αρχείο."""
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    """Φορτώνει το authentication token από το αρχείο."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def delete_token():
    """Διαγράφει το authentication token (logout)."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        
def login(username, password):
    """Σύνδεση χρήστη και αποθήκευση του authentication token."""
    data = {"username": username, "password": password}
    result = api_call("auth/login", method="POST", data=data)
    
    if result and "token" in result:
        save_token(result["token"])
        print("Login successful!")
        if username == "ADMIN":
            with open(ADMIN_ACCESS_FILE, "w") as f:
                f.write("1")
            print("You are logged in as ADMIN.")
    else:
        delete_token()
        print("Login failed. Check credentials.")

def logout():
    """Αποσύνδεση χρήστη και διαγραφή του authentication token."""
    result = api_call("auth/logout", method="POST", auth_required=True)

    # Αν το API επιστρέψει True (δηλ. status 204 ή 200 χωρίς JSON), θεωρούμε ότι πέτυχε
    if result is True:
        delete_token()
        if os.path.exists(ADMIN_ACCESS_FILE):
            os.remove(ADMIN_ACCESS_FILE)
        print("Logout successful!")
        return

    # Αν το API επιστρέψει error με status: failed
    if isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(f"Logout failed: {result.get('info', 'Unknown error')}")
        return

def check_admin_access():
    """Ελέγχει αν έχουμε πρόσβαση ως ADMIN."""
    return os.path.exists(ADMIN_ACCESS_FILE)

def usermod(username, password):
    """Δημιουργία νέου χρήστη ή αλλαγή κωδικού."""
    # Έλεγχος αν ο χρήστης υπάρχει
    result = api_call("admin/users", method="GET", auth_required=True)
    
    if result:
        # Αναζητούμε αν το username υπάρχει ήδη
        user_exists = any(user['username'] == username for user in result)
        
        if user_exists:
            # Αν υπάρχει, αλλάζουμε το password του χρήστη
            data = {"username": username, "password": password}
            update_result = api_call("admin/usermod", method="POST", data=data, auth_required=True)
            if update_result:
                print(f"Password for user {username} updated successfully!")
            else:
                print(f"Failed to update password for user {username}.")
        else:
            # Αν δεν υπάρχει, δημιουργούμε νέο χρήστη
            data = {"username": username, "password": password}
            create_result = api_call("admin/usermod", method="POST", data=data, auth_required=True)
            if create_result:
                print(f"User {username} created successfully!")
            else:
                print(f"Failed to create user {username}.")

def list_users():
    """Λίστα χρηστών"""
    result = api_call("admin/users", method="GET", auth_required=True)

    if result:
        print(result)
    else:
        print("Failed to retrieve users.")
        