'''
This module will provide the all functionalities that a user may need to 
perform using the Web Portal.
'''

import requests
import urllib3
import socket

IP = socket.gethostbyname(socket.gethostname())

API_LOGIN = "https://" + IP + ":9115/api/auth/login"
API_LOGOUT = "https://" + IP + ":9115/api/auth/logout"
API_DEBT_BASE = "https://" + IP + ":9115/api/owedBy"
API_STATIONS = "https://" + IP + ":9115/api/getTollStations"
API_OP_NAMES = "https://" + IP + ":9115/api/getOpNames"
API_PAYMENT = "https://" + IP + ":9115/api/makePayment"
API_STATION_INFO = "https://" + IP + ":9115/api/tollStationPasses"

# Disable warnings for SSL certificate verification
urllib3.disable_warnings()

# Function that retrieves the operator names from the API
# Return Values :
# Status Code : If the request failed
# dict : Operator names in the form of a dictionary
def getOpNames():
    response = requests.get(f"{API_OP_NAMES}", verify=False)
    if response.status_code != 200:
        return response.status_code
    return response.json()

# The user class represents a user object who can login and logout
# The user object stores the username, authentication status, and token
# The authenticated attribute should be used to check privileges for the user along with the username
# The token attribute should be used to make requests to the API whilst providing authentication
class User:
    # Constructor for the User object
    def __init__(self, user_data=None):
        if isinstance(user_data, dict):
            self.from_dict(user_data)
        else:
            self.username = user_data
            self.authenticated = False
            self.token = None
            self.opid = user_data
            self.opname = getOpNames().get(user_data, None)
    # Method to set the attributes of the user object from a dictionary
    def from_dict(self,data):
        self.username = data['username']
        self.authenticated = data['authenticated']
        self.token = data['token']
        self.opid = data['opid']
        self.opname = data['opname']
    # Method to return the attributes of the user object as a dictionary
    def to_dict(self):
        return {
            'username': self.username,
            'authenticated': self.authenticated,
            'token': self.token,
            'opid': self.opid,
            'opname': self.opname
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
            self.token = data.get("token", None)
            if self.token is not None:
                print("Login successful, token received.")
                self.authenticated = True
                return 1
            else:
                print("Login failed, no token received.")
                return -1
        else:
            print(f"Login failed with status code: {response.status_code}")
            return response.status_code

    # Method to logout the user
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
    
    # Method that calculates the amount that the user owes to the other operators
    # Within the specified date range
    # If the user is the admin, the function will return -1 (Admins cannot calculate charges)
    # Return Values : 
    # -1 : If the user is not authenticated or the user is the admin or the request failed
    # float : The amount that the user owes to the other operators
    def calcCharges(self, from_date, to_date):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        if self.opid == "ADMIN":
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
        return owed_to
    
    def calcStats(self, from_date, to_date, station_id):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        analytics_uri = f'{API_STATION_INFO}/{station_id}/{from_date}/{to_date}'
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.get(analytics_uri, headers=headers, verify=False)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        analytics = response.json()
        if self.opid == "ADMIN":
            total_revenue = sum([passing["passCharge"] for passing in analytics["passList"]], 0)
            analytics["totalRevenue"] = total_revenue
            return analytics
        if analytics.get("stationOperator", None) == self.opid:
            total_revenue = sum([passing["passCharge"] for passing in analytics["passList"]], 0)
            analytics["totalRevenue"] = total_revenue
        else:
            analytics["totalRevenue"] = None
        if analytics.get("stationOperator", None) != self.opid:
            new_passlist = [passing for passing in analytics["passList"] if passing.get("tagProvider", None) == self.opid]
            analytics["passList"] = new_passlist
        return analytics

    # Method to get the toll stations all toll Stations from the API
    # Return Values : 
    # -1 : If the user is not authenticated or the request failed
    # dict : The toll stations in the form of a dictionary
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
    
    def makePayment(self, operator, start_date, end_date):
        # Send the POST request with with token in X-OBSERVATORY-AUTH header
        full_uri = f"{API_PAYMENT}/{self.opid}/{operator}/{start_date}/{end_date}"
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.post(full_uri, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"Error in response for operator {operator}")
            print(response.text)
            return response
        return response
            
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