'''
This module will provide the all functionalities that a user may need to 
perform using the Web Portal.
'''

import os
import requests
import urllib3
import socket

IP = socket.gethostbyname(socket.gethostname())

API_LOGIN = "https://" + IP + ":9115/api/auth/login"
API_LOGOUT = "https://" + IP + ":9115/api/auth/logout"
API_DEBT_BASE = "https://" + IP + ":9115/api/owedBy"
API_STATIONS = "https://" + IP + ":9115/api/getTollStations"
API_OP_NAMES = "https://" + IP + ":9115/api/getOpNames"

print(API_LOGIN)

urllib3.disable_warnings()

def getOpNames():
    response = requests.get(f"{API_OP_NAMES}", verify=False)
    print(response)
    if response.status_code != 200:
        print("Error in response")
        print(response.text)
        return -1
    return response.json()

# The user class represents a user object who can login and logout
# The user object stores the username, authentication status, and token
# The authenticated attribute should be used to check privileges for the user along with the username
class User:
    def __init__(self, username):
        self.username = username
        self.authenticated = False
        self.token = None
        self.opid = username
        self.opname = getOpNames().get(username, None)
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
        if user.opid == "ADMIN":
            # Maybe we should implement a method to calculate charges for all operators
            # So that the admin can see the charges for all operators
            print("Admin user cannot calculate charges")
            return -1
        opID = self.opid
        final_url = f"{API_DEBT_BASE}/{opID}/{from_date}/{to_date}"
        response = requests.get(final_url, verify=False)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        data = response.json()
        owed_to = data["owedTo"]
        print(f"Owed to: {owed_to}") # For debugging
        return owed_to
    def calcStats(self, from_date, to_date):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        opID = self.opid
        final_url = f"{API_DEBT_BASE}/{opID}/{from_date}/{to_date}"
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
    def getStations(self):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        response = requests.get(API_STATIONS, verify=False)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        data = response.json()
        return data
    
if __name__ == "__main__":
    # Quick Test of the functionality
    user = User("NAO")
    token = user.authenticate("default_password")
    if token != -1:
        print(f"Token received: {token}")
    else:
        print("Authentication failed.")
    user_charges = user.calcCharges("20220101", "20220115")
    print(user_charges)
    logout = user.logout()