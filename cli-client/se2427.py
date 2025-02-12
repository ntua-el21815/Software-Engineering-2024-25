import argparse
from api_requests import api_call, login, logout, check_admin_access, list_users, upload_passes_csv, usermod
import json
import os
import requests
import socket
import csv
import sys

ip = socket.gethostbyname(socket.gethostname())
BASE_URL = f"https://{ip}:9115/api"

def healthcheck():
    """Έλεγχος συνδεσιμότητας του συστήματος."""
    result = api_call("admin/healthcheck")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def resetpasses():
    """Επαναφορά δεδομένων διελεύσεων."""
    result = api_call("admin/resetpasses", method="POST")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def resetstations(file_path):
    """Επαναφορά δεδομένων σταθμών διοδίων με το αρχείο CSV."""
    url = f"{BASE_URL}/admin/resetstations"
    print(f"URL: {url}")
    
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'), 'text/csv')}

    try:
        response = api_call("admin/resetstations", method="POST")
        
        if response and response.get("status") == "OK":
            print("Stations reset successfully.")
        else:
            print(f"Failed to reset stations: {response.get('info', 'No error details provided.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    finally:
        files['file'][1].close()

def tollstationpasses(station, date_from, date_to, output_format="csv"):
    """Ανάκτηση διελεύσεων για συγκεκριμένο σταθμό και περίοδο."""
    result = api_call(f"tollStationPasses/{station}/{date_from}/{date_to}", params={"format": output_format})

    if result is None or result == "":
        print("No data available or API error.")
        return

    if isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if isinstance(result, str) and result.startswith("passIndex,"):
        print(result)
        return

    if isinstance(result, dict) and "nPasses" in result and result["nPasses"] == 0:
        print("passIndex,passID,timestamp,tagID,tagProvider,passType,passCharge")
        return

    print(f"Unexpected API response format: {json.dumps(result, indent=2, ensure_ascii=False)}")

def passanalysis(station_op, tag_op, date_from, date_to, output_format="csv"):
    """Ανάλυση διελεύσεων μεταξύ δύο operators."""
    result = api_call(f"passAnalysis/{station_op}/{tag_op}/{date_from}/{date_to}", params={"format": output_format})

    if result is None or result == "":
        print("No data available or API error.")
        return

    if isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if isinstance(result, str) and result.startswith("passIndex,"):
        print(result)
        return

    if isinstance(result, dict) and "nPasses" in result and result["nPasses"] == 0:
        print("passIndex,passID,stationID,timestamp,tagID,passCharge")
        return

    print(f"Unexpected API response format: {json.dumps(result, indent=2, ensure_ascii=False)}")

def passescost(station_op, tag_op, date_from, date_to, output_format="csv"):
    """Υπολογισμός κόστους διελεύσεων μεταξύ operators."""
    result = api_call(f"passesCost/{station_op}/{tag_op}/{date_from}/{date_to}")

    if result is None or result == {}:
        print("No cost data available for these operators in the given period.")
        return

    if isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if isinstance(result, dict) and "passesCost" in result:
        filtered_result = {
            "tollOpID": result.get("tollOpID", "UNKNOWN"),
            "tagOpID": result.get("tagOpID", "UNKNOWN"),
            "periodFrom": result.get("periodFrom", ""),
            "periodTo": result.get("periodTo", ""),
            "nPasses": result.get("nPasses", 0),
            "passesCost": result.get("passesCost", 0.0)
        }

        if output_format == "csv":
            fieldnames = ["tollOpID", "tagOpID", "periodFrom", "periodTo", "nPasses", "passesCost"]
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(filtered_result)
        else:
            print(json.dumps(filtered_result, indent=2, ensure_ascii=False))
        return

    print(f"Unexpected API response format: {json.dumps(result, indent=2, ensure_ascii=False)}")

def chargesby(toll_op, date_from, date_to, output_format="csv"):
    """Λίστα διελεύσεων από άλλους operators και χρεώσεις."""
    result = api_call(f"chargesBy/{toll_op}/{date_from}/{date_to}", params={"format": output_format})

    if result is None or result == "":
        print("No data available or API error.")
        return

    if isinstance(result, dict) and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if isinstance(result, str) and result.startswith("visitingOpID,"):
        print(result)
        return

    if isinstance(result, dict) and "vOpList" in result:
        data_list = result["vOpList"]
        
        if not data_list:
            print("visitingOpID,nPasses,passesCost")
            return

        csv_output = "visitingOpID,nPasses,passesCost\n"
        for entry in data_list:
            csv_output += f"{entry.get('visitingOpID', '')},{entry.get('nPasses', 0)},{entry.get('passesCost', 0.0)}\n"
        
        print(csv_output.strip())
        return

    print(f"Unexpected API response format: {json.dumps(result, indent=2, ensure_ascii=False)}")

def addpasses(file_path):
    """Ανεβάζει διελεύσεις από CSV αρχείο στο σύστημα. Μόνο οι ADMIN μπορούν να το κάνουν."""
    
    if not check_admin_access():
        return

    if not os.path.exists(file_path):
        print(f"The file '{file_path}' was not found.")
        return
    
    result = upload_passes_csv(file_path)
    
    if result:
        print("Passes uploaded successfully!")
    else:
        print("Failed to upload passes. Check the CSV format and try again.")

def parse_args():
    parser = argparse.ArgumentParser(description="Command Line Interface for Toll System")
    subparsers = parser.add_subparsers(dest="command")

    valid_commands = [
        "healthcheck", "resetpasses", "resetstations", "tollstationpasses",
        "passanalysis", "passescost", "chargesby", "login", "logout", "admin"
    ]

    subparsers.add_parser("healthcheck", help="Check system health")
    subparsers.add_parser("resetpasses", help="Reset all pass data")

    resetstations_parser = subparsers.add_parser("resetstations", help="Reset toll station data with a CSV file")
    resetstations_parser.add_argument("--file", default="tollstations2024.csv", help="Path to the CSV file")

    station_parser = subparsers.add_parser("tollstationpasses", help="Retrieve toll station passes")
    station_parser.add_argument("--station", required=True, help="Toll station ID")
    station_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    station_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    station_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    pass_parser = subparsers.add_parser("passanalysis", help="Analyze pass data between operators")
    pass_parser.add_argument("--stationop", required=True, help="Station operator ID")
    pass_parser.add_argument("--tagop", required=True, help="Tag operator ID")
    pass_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    pass_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    pass_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    cost_parser = subparsers.add_parser("passescost", help="Calculate pass cost between operators")
    cost_parser.add_argument("--stationop", required=True, help="Station operator ID")
    cost_parser.add_argument("--tagop", required=True, help="Tag operator ID")
    cost_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    cost_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    cost_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    charges_parser = subparsers.add_parser("chargesby", help="Retrieve charges by other operators")
    charges_parser.add_argument("--opid", required=True, help="Operator ID")
    charges_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    charges_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    charges_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")
    
    login_parser = subparsers.add_parser("login", help="User login")
    login_parser.add_argument("--username", required=True, help="Username")
    login_parser.add_argument("--passw", required=True, help="Password")

    subparsers.add_parser("logout", help="User logout")

    admin_parser = subparsers.add_parser("admin", help="User management")
    admin_parser.add_argument("--usermod", action="store_true", help="Modify user")
    admin_parser.add_argument("--username", help="Username")
    admin_parser.add_argument("--passw", help="New password")
    admin_parser.add_argument("--users", action="store_true", help="List users")
    admin_parser.add_argument("--addpasses", action="store_true", help="Upload passes from CSV file")
    admin_parser.add_argument("--source", help="Path to the CSV file")
    
    if len(sys.argv) > 1 and sys.argv[1] not in valid_commands:
        print(f"Unknown command: '{sys.argv[1]}'.")
        sys.exit(1)

    try:
        return parser.parse_args()
    except SystemExit as e:
        if "--format" in sys.argv:
            invalid_index = sys.argv.index("--format") + 1
            if invalid_index < len(sys.argv):
                invalid_format = sys.argv[invalid_index]
                print(f"format '{invalid_format}' is not valid. Choose from: json, csv")
            else:
                print("format argument is missing a value.")
        else:
            print("Invalid command or arguments.")
        sys.exit(1)

    return parser.parse_args()

def main():
    args = parse_args()

    if args.command is None:
        print("No command provided.")
        return
    
    if args.command == "healthcheck":
        healthcheck()
    elif args.command == "resetpasses":
        resetpasses()
    elif args.command == "resetstations":
        resetstations("tollstations2024.csv")
    elif args.command == "tollstationpasses":
        tollstationpasses(args.station, args.date_from, args.date_to, args.format)
    elif args.command == "passanalysis":
        passanalysis(args.stationop, args.tagop, args.date_from, args.date_to, args.format)
    elif args.command == "passescost":
        passescost(args.stationop, args.tagop, args.date_from, args.date_to, args.format)
    elif args.command == "chargesby":
        chargesby(args.opid, args.date_from, args.date_to, args.format)
    elif args.command == "addpasses":
        addpasses(args.source)
    elif args.command == "login":
        login(args.username, args.passw)
    elif args.command == "logout":
        logout()
    elif args.command == "admin":
        if not check_admin_access():
            return 
        if args.usermod:
            if args.username and args.passw:
                usermod(args.username, args.passw)
            else:
                print("Please provide both --username and --passw for usermod.")
        elif args.users:
            list_users()
        elif args.addpasses:
            if args.source:
                addpasses(args.source)
            else:
                print("Error: --source is required for uploading passes.")
        else:
            print("Invalid admin command. Use --usermod or --users or --addpasses.")

if __name__ == "__main__":
    main()