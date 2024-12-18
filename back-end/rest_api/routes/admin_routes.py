from flask import Blueprint, jsonify
from models import db, Pass, Tag, TollOperator, TollStation
from flask import request
import pandas as pd
from datetime import datetime

admin_routes = Blueprint('admin_routes', __name__)

# Healthcheck
@admin_routes.route('/healthcheck', methods=['GET'])
def healthcheck():
    try:
        n_stations = db.session.query(Tag).count()
        return jsonify({"status": "OK", "n_tags": n_stations}), 200
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500
    

# Reset stations from CSV
@admin_routes.route('/resetstations', methods=['POST'])
def reset_stations():
    try:
        # Έλεγχος αν υπάρχει το αρχείο
        if 'file' not in request.files:
            return jsonify({"status": "failed", "info": "No file part"}), 400

        file = request.files['file']

        # Έλεγχος ονόματος αρχείου και τύπου
        if file.filename == '' or not file.filename.endswith('.csv'):
            return jsonify({"status": "failed", "info": "Invalid file format"}), 400

        # Ανάγνωση του αρχείου CSV
        df = pd.read_csv(file)

        # Έλεγχος για τα απαιτούμενα πεδία
        required_columns = {'Toll_Station_ID', 'Toll_OperatorOperator_ID', 'Name', 'Locality',
                            'Road', 'Latitude', 'Longitude', 'Type', 'Price1', 'Price2', 'Price3', 'Price4'}
        if not required_columns.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Invalid CSV format"}), 400

        # Διαγραφή όλων των εγγραφών στον πίνακα Toll_Station
        db.session.query(TollStation).delete()

        # Εισαγωγή νέων δεδομένων από το CSV
        for _, row in df.iterrows():
            new_station = TollStation(
                Toll_Station_ID=row['Toll_Station_ID'],
                Toll_OperatorOperator_ID=row['Toll_OperatorOperator_ID'],
                Name=row['Name'],
                Locality=row['Locality'],
                Road=row['Road'],
                Latitude=row['Latitude'],
                Longitude=row['Longitude'],
                Type=row['Type'],
                Price1=row['Price1'],
                Price2=row['Price2'],
                Price3=row['Price3'],
                Price4=row['Price4']
            )
            db.session.add(new_station)

        db.session.commit()
        return jsonify({"status": "OK"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500

# Reset passes and tags
@admin_routes.route('/resetpasses', methods=['POST'])
def reset_passes():
    try:
        # Διαγραφή όλων των εγγραφών από Pass και Tag
        db.session.query(Pass).delete()
        db.session.query(Tag).delete()

        # Προαιρετική δημιουργία διαχειριστικού λογαριασμού
        admin_exists = db.session.query(TollOperator).filter_by(Operator_ID='admin').first()
        if not admin_exists:
            admin_user = TollOperator(
                Operator_ID='admin',
                Name='Administrator',
                email='admin@example.com',
                password='freepasses4all'  # Προσοχή: Στην παραγωγή, θα έπρεπε να είναι hashed!
            )
            db.session.add(admin_user)

        db.session.commit()
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500
    

# Add passes from CSV
@admin_routes.route('/addpasses', methods=['POST'])
def add_passes():
    try:
        # Έλεγχος αν έχει ανεβεί αρχείο
        if 'file' not in request.files:
            return jsonify({"status": "failed", "info": "No file part"}), 400

        file = request.files['file']

        # Έλεγχος τύπου αρχείου
        if file.filename == '' or not file.filename.endswith('.csv'):
            return jsonify({"status": "failed", "info": "Invalid file format"}), 400

        # Ανάγνωση του αρχείου CSV με pandas
        df = pd.read_csv(file)

        # Έλεγχος στήλων CSV
        required_columns = {'tag_ID', 'timestamp', 'charge', 'Toll_Station_ID'}
        if not required_columns.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Invalid CSV format"}), 400

        # Εισαγωγή δεδομένων στη βάση
        for _, row in df.iterrows():
            new_pass = Pass(
                tag_ID=row['tag_ID'],
                timestamp=datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
                charge=row['charge'],
                Toll_Station_ID=row['Toll_Station_ID']
            )
            db.session.add(new_pass)

        db.session.commit()
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500
    

