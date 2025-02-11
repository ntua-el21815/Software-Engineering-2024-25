import argparse
from api_requests import api_call, login, logout, check_admin_access, list_users, upload_passes_csv, usermod
import json
import os
import requests
import socket
import csv
import sys

def json_to_csv(json_data, params={}):
    """Μετατρέπει JSON δεδομένα σε CSV και διατηρεί τα πεδία εισόδου όταν δεν υπάρχουν δεδομένα."""
    if not json_data:
        print("No data available.")
        return

    # Αν υπάρχει error από το API
    if isinstance(json_data, dict) and "info" in json_data and "status" in json_data and json_data["status"] == "failed":
        print(json_data["info"])
        return

    if isinstance(json_data, dict) and "passesCost" in json_data:
        fieldnames = ["tollOpID", "tagOpID", "periodFrom", "periodTo", "nPasses", "passesCost"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "tollOpID": json_data.get("tollOpID", "UNKNOWN"),
            "tagOpID": json_data.get("tagOpID", "UNKNOWN"),
            "periodFrom": json_data.get("periodFrom", ""),
            "periodTo": json_data.get("periodTo", ""),
            "nPasses": json_data.get("nPasses", 0),
            "passesCost": json_data.get("passesCost", 0.0)
        })
        return

    # ✅ Ανάλυση δεδομένων όταν δεν υπάρχουν διελεύσεις
    if "nPasses" in json_data and json_data["nPasses"] == 0:
        # Προσδιορισμός αν η κλήση προέρχεται από passanalysis ή passescost
        if "stationOp" in params and "tagOp" in params:
            fieldnames = ["stationOp", "tagOp", "periodFrom", "periodTo", "nPasses"]
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "stationOp": params.get("stationOp", "UNKNOWN"),
                "tagOp": params.get("tagOp", "UNKNOWN"),
                "periodFrom": json_data.get("periodFrom", params.get("date_from", "")),
                "periodTo": json_data.get("periodTo", params.get("date_to", "")),
                "nPasses": json_data.get("nPasses", 0)
            })
        else:
            # Default έξοδος για tollstationpasses
            fieldnames = ["stationID", "periodFrom", "periodTo", "nPasses"]
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "stationID": json_data.get("stationID", params.get("station", "UNKNOWN")),
                "periodFrom": json_data.get("periodFrom", ""),
                "periodTo": json_data.get("periodTo", ""),
                "nPasses": json_data.get("nPasses", 0)
            })
        return

    # ✅ Αν υπάρχουν κανονικά δεδομένα
    if "passList" in json_data:
        data_list = json_data["passList"]
        if not data_list:
            print("No data available.")
            return
    else:
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        return

    fieldnames = list(data_list[0].keys())  # Αποφυγή KeyError
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data_list)

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
    
    headers = {}
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'), 'text/csv')}
    
    try:
        response = requests.post(url, files=files, headers=headers, verify=False)
        
        # Ελέγχουμε την απάντηση του API
        if response.status_code == 200:
            print("Reset stations successful")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Failed to reset stations. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    finally:
        files['file'][1].close()

def tollstationpasses(station, date_from, date_to, output_format="csv"):
    """Ανάκτηση διελεύσεων για συγκεκριμένο σταθμό και περίοδο."""
    result = api_call(f"tollStationPasses/{station}/{date_from}/{date_to}", params={"format": output_format})

    # Έλεγχος αν το API επέστρεψε error
    if isinstance(result, dict) and "info" in result and "status" in result and result["status"] == "failed":
        print(result["info"])  # ✅ Εμφάνιση του error message από το API
        return

    if result:
        if output_format == "csv":
            if isinstance(result, str) and result.startswith("{"):  
                try:
                    json_data = json.loads(result)
                    json_to_csv(json_data, params={"station": station})
                except json.JSONDecodeError:
                    print(result)  # Αν η απάντηση είναι ήδη CSV, την εκτυπώνουμε
            else:
                print(result)  # Αν είναι ήδη CSV, εκτύπωση απευθείας
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))  # Εκτύπωση JSON αν ζητήθηκε
    else:
        print("No data available.")

def passanalysis(station_op, tag_op, date_from, date_to, output_format="csv"):
    """Ανάλυση διελεύσεων μεταξύ δύο operators."""
    result = api_call(f"passAnalysis/{station_op}/{tag_op}/{date_from}/{date_to}", params={"format": output_format})

    if isinstance(result, dict) and "info" in result and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if result:
        if output_format == "csv":
            if isinstance(result, str) and result.startswith("{"):
                try:
                    json_data = json.loads(result)
                    json_to_csv(json_data, params={
                        "stationOp": station_op,
                        "tagOp": tag_op,
                        "date_from": date_from,
                        "date_to": date_to
                    })
                except json.JSONDecodeError:
                    print(result)  # Αν είναι ήδη CSV, εκτύπωση απευθείας
            else:
                print(result)
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("No data available.")

def passescost(station_op, tag_op, date_from, date_to, output_format="csv"):
    """Υπολογισμός κόστους διελεύσεων μεταξύ operators."""
    result = api_call(f"passesCost/{station_op}/{tag_op}/{date_from}/{date_to}", params={"format": output_format})

    if isinstance(result, dict) and "info" in result and "status" in result and result["status"] == "failed":
        print(result["info"])
        return

    if result:
        if output_format == "csv":
            # ✅ Έλεγχος αν το API επιστρέφει JSON αντί για CSV
            if isinstance(result, str):
                try:
                    json_data = json.loads(result)
                    json_to_csv(json_data, params={
                        "stationOp": station_op,
                        "tagOp": tag_op,
                        "date_from": date_from,
                        "date_to": date_to
                    })
                except json.JSONDecodeError:
                    print(result)  # ✅ Αν είναι ήδη CSV, εκτύπωση απευθείας
            else:
                json_to_csv(result, params={
                    "stationOp": station_op,
                    "tagOp": tag_op,
                    "date_from": date_from,
                    "date_to": date_to
                })
        else:
            # ✅ Εκτύπωση JSON αν ζητηθεί
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("No data available.")

def chargesby(toll_op, date_from, date_to, output_format="csv"):
    """Λίστα διελεύσεων από άλλους operators και χρεώσεις."""
    result = api_call(f"chargesBy/{toll_op}/{date_from}/{date_to}", params={"format": output_format})

    # ✅ Έλεγχος αν η απάντηση είναι string (και όχι JSON)
    if isinstance(result, str):
        try:
            result = json.loads(result)  # Προσπαθούμε να το μετατρέψουμε σε JSON
        except json.JSONDecodeError:
            print(f"Unexpected API response: {result}")  # Εκτύπωση raw response αν δεν είναι JSON
            return

    # ✅ Έλεγχος αν το API επέστρεψε error (π.χ. μη έγκυρο opid)
    if isinstance(result, dict) and "info" in result and "status" in result and result["status"] == "failed":
        print(f"Error: {result['info']}")  # Εμφάνιση error και έξοδος χωρίς CSV/JSON
        return

    # ✅ Αν δεν υπάρχουν operators (επιστρέφουμε `nOperators=0`)
    if isinstance(result, dict) and "vOpList" in result:
        data_list = result["vOpList"]
        if not data_list:
            # ✅ Εμφανίζουμε το κανονικό CSV/JSON με `nOperators=0`
            response_data = {
                "tollOpID": toll_op,
                "periodFrom": result.get("periodFrom", date_from),
                "periodTo": result.get("periodTo", date_to),
                "nOperators": 0
            }

            if output_format == "json":
                print(json.dumps(response_data, indent=2, ensure_ascii=False))  # JSON output
            else:
                fieldnames = ["tollOpID", "periodFrom", "periodTo", "nOperators"]
                writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(response_data)

            return

        else:
            # ✅ Κανονική εκτύπωση δεδομένων αν υπάρχουν
            if output_format == "json":
                print(json.dumps(result, indent=2, ensure_ascii=False))  # JSON output
            else:
                json_to_csv(result, params={"tollOpID": toll_op})
            return

    # ✅ Αν τίποτα από τα παραπάνω δεν ισχύει, σημαίνει ότι το API δεν απάντησε σωστά
    print(f"Unexpected API response: {json.dumps(result, indent=2)}")

def addpasses(file_path):
    """Ανεβάζει διελεύσεις από CSV αρχείο στο σύστημα."""
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

    # Διαχείριση Συστήματος
    subparsers.add_parser("healthcheck", help="Check system health")
    subparsers.add_parser("resetpasses", help="Reset all pass data")

    # Reset Stations
    resetstations_parser = subparsers.add_parser("resetstations", help="Reset toll station data with a CSV file")
    resetstations_parser.add_argument("--file", default="tollstations2024.csv", help="Path to the CSV file")

    # Ανάκτηση διελεύσεων
    station_parser = subparsers.add_parser("tollstationpasses", help="Retrieve toll station passes")
    station_parser.add_argument("--station", required=True, help="Toll station ID")
    station_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    station_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    station_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    # Ανάλυση διελεύσεων μεταξύ δύο operators
    pass_parser = subparsers.add_parser("passanalysis", help="Analyze pass data between operators")
    pass_parser.add_argument("--stationop", required=True, help="Station operator ID")
    pass_parser.add_argument("--tagop", required=True, help="Tag operator ID")
    pass_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    pass_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    pass_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    # Υπολογισμός κόστους διελεύσεων μεταξύ δύο operators
    cost_parser = subparsers.add_parser("passescost", help="Calculate pass cost between operators")
    cost_parser.add_argument("--stationop", required=True, help="Station operator ID")
    cost_parser.add_argument("--tagop", required=True, help="Tag operator ID")
    cost_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    cost_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    cost_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")

    # Λίστα διελεύσεων από άλλους operators
    charges_parser = subparsers.add_parser("chargesby", help="Retrieve charges by other operators")
    charges_parser.add_argument("--opid", required=True, help="Operator ID")
    charges_parser.add_argument("--from", dest="date_from", required=True, help="Start date (YYYYMMDD)")
    charges_parser.add_argument("--to", dest="date_to", required=True, help="End date (YYYYMMDD)")
    charges_parser.add_argument("--format", choices=["json", "csv"], default="csv", help="Output format")
    
    # Authentication
    login_parser = subparsers.add_parser("login", help="User login")
    login_parser.add_argument("--username", required=True, help="Username")
    login_parser.add_argument("--passw", required=True, help="Password")

    subparsers.add_parser("logout", help="User logout")

    # Διαχείριση χρηστών
    admin_parser = subparsers.add_parser("admin", help="User management")
    admin_parser.add_argument("--usermod", action="store_true", help="Modify user")
    admin_parser.add_argument("--username", help="Username")
    admin_parser.add_argument("--passw", help="New password")
    admin_parser.add_argument("--users", action="store_true", help="List users")
    admin_parser.add_argument("--addpasses", action="store_true", help="Upload passes from CSV file")
    admin_parser.add_argument("--source", help="Path to the CSV file")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in valid_commands:
        print(f"Unknown command: '{sys.argv[1]}'.")
        sys.exit(1)

    return parser.parse_args()
    
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
            print("You must be logged in as ADMIN to access admin commands.")
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