import requests
import os
import urllib3
import warnings
import socket

warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
finally:
    s.close()
    
BASE_URL = f"https://{ip}:9115/api"
TOKEN_FILE = "auth_token.txt"
ADMIN_ACCESS_FILE = "admin_access.txt"

def get_token():
    """Διαβάζει το αποθηκευμένο JWT token από το αρχείο."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def api_call(endpoint, method="GET", data=None, params=None):
    """Γενική συνάρτηση για κλήσεις στο API με Authentication."""
    url = f"{BASE_URL}/{endpoint}"
    token = get_token()
    headers = {"Content-Type": "application/json"}

    if token:
        headers["X-OBSERVATORY-AUTH"] = token

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, verify=False)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, verify=False)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        else:
            raise ValueError("Unsupported HTTP method")

        # ✅ Αν το API επιστρέψει 204 No Content ή είναι κενό response, επιστρέφουμε None
        if response.status_code == 204 or not response.text.strip():
            return None

        # ✅ Αν η απάντηση είναι CSV (και όχι JSON), την επιστρέφουμε ως raw text
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/csv" in content_type or response.text.startswith("passIndex,"):
            return response.text  # ✅ Επιστροφή CSV ως απλό string

        # ✅ Προσπάθεια μετατροπής σε JSON
        return response.json()

    except requests.exceptions.JSONDecodeError:
        print(f"❌ API returned non-JSON response: {response.text}")
        return response.text  # ✅ Επιστροφή απλού text αν δεν είναι JSON

    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return None
    
def upload_passes_csv(file_path):
    """Στέλνει αρχείο CSV στο API για εισαγωγή διελεύσεων."""
    url = f"{BASE_URL}/admin/addpasses"
    token = get_token()

    headers = {"X-OBSERVATORY-AUTH": token} if token else {}

    with open(file_path, "rb") as file:
        files = {"file": (file_path, file, "text/csv")}
        
        try:
            response = requests.post(url, headers=headers, files=files, verify=False)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            return None

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

    if os.path.exists(TOKEN_FILE):
        print("You are already logged in. Please logout first before logging in again.")
        return
    
    data = {"username": username, "password": password}

    response = requests.post(f"{BASE_URL}/login", data=data, verify=False)
    if response.status_code == 200:
        result = response.json()
        if "token" in result:
            save_token(result["token"])
            print("Login successful!")
            if username == "ADMIN":
                with open(ADMIN_ACCESS_FILE, "w") as f:
                    f.write("1")
                print("You are logged in as ADMIN.")
        else:
            delete_token()
            print("Login failed. Check credentials.")
    else:
        delete_token()
        print("Login failed. Check credentials.")

def logout():
    """Αποσύνδεση χρήστη και διαγραφή του authentication token."""
    result = api_call("logout", method="POST")

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    if os.path.exists(ADMIN_ACCESS_FILE):
        os.remove(ADMIN_ACCESS_FILE)

    if result is None:
        print("Logout successful!")
    elif isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(f"Logout failed: {result.get('info', 'Unknown error')}")
    else:
        print("Logout successful!")

def check_admin_access():
    """Ελέγχει αν ο χρήστης είναι συνδεδεμένος ως ADMIN."""
    if not os.path.exists(TOKEN_FILE):
        print("No authentication token found. Please login first.")
        return False
    
    if not os.path.exists(ADMIN_ACCESS_FILE):
        print("You must be logged in as ADMIN to access this command.")
        return False
    
    return True

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
        