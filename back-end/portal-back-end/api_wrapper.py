'''
This module will provide all functionalities that a user may need 
to perform using the Web Portal.
'''

import requests
import urllib3
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('8.8.8.8', 80))
    IP = s.getsockname()[0]
finally:
    s.close()

API_LOGIN = "https://" + IP + ":9115/api/login"
API_LOGOUT = "https://" + IP + ":9115/api/logout"
API_DEBT_BASE = "https://" + IP + ":9115/api/owedBy"
API_STATIONS = "https://" + IP + ":9115/api/getTollStations"
API_OP_NAMES = "https://" + IP + ":9115/api/getOpNames"
API_PAYMENT = "https://" + IP + ":9115/api/makePayment"
API_STATION_INFO = "https://" + IP + ":9115/api/tollStationPasses"

# Disable warnings for SSL certificate verification
urllib3.disable_warnings()

def getOpNames():
    response = requests.get(f"{API_OP_NAMES}", verify=False)
    if response.status_code != 200:
        return response.status_code
    return response.json()

class User:
    def __init__(self, user_data=None):
        if isinstance(user_data, dict):
            self.from_dict(user_data)
        else:
            self.username = user_data
            self.authenticated = False
            self.token = None
            self.opid = user_data
            self.opname = getOpNames().get(user_data, None)

    def from_dict(self, data):
        self.username = data['username']
        self.authenticated = data['authenticated']
        self.token = data['token']
        self.opid = data['opid']
        self.opname = data['opname']

    def to_dict(self):
        return {
            'username': self.username,
            'authenticated': self.authenticated,
            'token': self.token,
            'opid': self.opid,
            'opname': self.opname
        }
    
    def authenticate(self, password):
        self.authenticated = False
        self.token = None
        payload = {
            'username': self.username,
            'password': password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(API_LOGIN, data=payload, headers=headers, verify=False)
        if response.status_code == 200:
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

    def logout(self):
        if not self.token:
            print("No token to logout.")
            return -1
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.post(API_LOGOUT, headers=headers, verify=False)
        if response.status_code == 200:
            print("Logout successful.")
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
        if self.opid == "ADMIN":
            print("Admin user cannot calculate charges")
            return -1
        opID = self.opid
        final_url = f"{API_DEBT_BASE}/{opID}/{from_date}/{to_date}"
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.get(final_url, headers=headers, verify=False)
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

    def getStations(self):
        if not self.authenticated:
            print("User not authenticated")
            return -1
        headers = {
            "X-OBSERVATORY-AUTH": self.token
        }
        response = requests.get(API_STATIONS, headers=headers, verify=False)
        if response.status_code != 200:
            print("Error in response")
            print(response.text)
            return -1
        data = response.json()
        return data
    
    def makePayment(self, operator, start_date, end_date):
        if not self.authenticated:
            print("User not authenticated")
            return -1
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