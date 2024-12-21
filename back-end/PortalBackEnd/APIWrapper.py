'''
This module will provide the all functionalities that a user may need to 
perform using the Web Portal.
'''

API_LOGIN = "http://localhost:9115/api/auth/login"
API_LOGOUT = "http://localhost:9115/api/auth/logout"
API_CHARGES_BASE = "http://localhost:9115/api/chargesBy"

import requests

# The user class represents a user object who can login and logout
# The user object stores the username, authentication status, and token
# The authenticated attribute should be used to check privileges for the user along with the username
class User:
    def __init__(self, username):
        self.username = username
        self.authenticated = False
        self.token = None
        self.opid = username
    def from_dict(self,data):
        self.username = data['username']
        self.authenticated = data['authenticated']
        self.token = data['token']
        self.opid = data['opid']
    def to_dict(self):
        return {
            'username': self.username,
            'authenticated': self.authenticated,
            'token': self.token,
            'opid': self.opid
        }
    # Method to authenticate the user and get the token
    # Returns the token if successful, -1 if token is invalid, or the status code if the request failed
    def authenticate(self, password):
        
        self.authenticated = False
        self.token = None

        # Data to be sent in the request body (username, password) encoded as x-www-form-urlencoded
        payload = {
            'username': self.username,
            'password': password
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"  # Explicitly setting the content type
        }

        # Sending POST request with the data and headers
        response = requests.post(API_LOGIN, data=payload, headers=headers, verify=False)

        # Check if the authentication is successful
        if response.status_code == 200:
            # Parse the JSON response to get the token
            data = response.json()
            self.token = data.get("token")
            if self.token is not None:
                print("Login successful, token received.")
                self.authenticated = True
                return 1
            else:
                print("Login failed, no token received.")
                return -1
        else:
            print(f"Login failed with status code: {response.status_code}")
            return -1

    # Function to logout the user
    # Returns 1 if successful, or the status code if the request failed
    def logout(self):
        # Send the POST request with with token in X-OBSERVATORY-AUTH header
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.post(API_LOGOUT, headers=headers, verify=False)
        if response.status_code == 200:
            print("Logout successful.")
            # Reset the user's attributes since the object is no longer valid
            self.authenticated = False
            self.token = None
            self.username = None
            return 1
        else:
            print(f"Logout failed with status code: {response.status_code}")
            print(response.text)
            print("token:", self.token)
            return response.status_code
    def calcCharges(self, from_date, to_date):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        opID = self.opid
        final_url = f"{API_CHARGES_BASE}/{opID}/{from_date}/{to_date}"
        response = requests.get(final_url)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        data = response.json()
        # Remove the operator that is our user from the JSON response
        data["vOpList"] = [item for item in data["vOpList"] if item["visitingOpID"] != self.opid]
        return data
    def calcStats(self, from_date, to_date):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        opID = self.opid
        final_url = f"{API_CHARGES_BASE}/{opID}/{from_date}/{to_date}"
        response = requests.get(final_url)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        data = response.json()
        charge_per_operator = data["vOpList"]
        total_cost = sum(item["passesCost"] for item in charge_per_operator)
        # Printing the percentage of the total cost for each operator
        for item in charge_per_operator:
            print(f"Operator: {item['visitingOpID']}, Cost: {item['passesCost']}, Percentage: {item['passesCost']/total_cost*100}%")
        return data
    
if __name__ == "__main__":
    # Quick Test of the functionality
    user = User("MO")
    token = user.authenticate("default_password")
    if token != -1:
        print(f"Token received: {token}")
    else:
        print("Authentication failed.")
    user_charges = user.calcCharges("20220101", "20220131", "all")
    print(user_charges)
    user.calcStats("20220101", "20220131", "all")
    logout = user.logout()