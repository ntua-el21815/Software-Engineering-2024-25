from flask import Blueprint, jsonify
from models import db, Pass, Tag, TollOperator, TollStation, Debt
from flask import request
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import os
from routes.auth_routes import token_required 

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/healthcheck', methods=['GET'])
@token_required
def healthcheck():
    try:
       
        db.session.execute(text('SELECT 1'))  


        n_stations = db.session.query(TollStation).count()  
        n_tags = db.session.query(Tag).count()  
        n_passes = db.session.query(Pass).count()  

        connection_string = db.engine.url

        return jsonify({
            "status": "OK",
            "dbconnection": str(connection_string),
            "n_stations": n_stations,
            "n_tags": n_tags,
            "n_passes": n_passes
        }), 200

    except SQLAlchemyError as e:
        # Σε περίπτωση αποτυχίας σύνδεσης με τη βάση
        connection_string = db.engine.url
        return jsonify({
            "status": "failed",
            "dbconnection": str(connection_string),
            "info": str(e)
        }), 401
    


CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "tollstations2024.csv")

@admin_routes.route('/resetstations', methods=['POST'])
@token_required
def reset_stations():
    try:

        if not os.path.exists(CSV_FILE_PATH):
            return jsonify({"status": "failed", "info": f"File not found: {CSV_FILE_PATH}"}), 400

        df = pd.read_csv(CSV_FILE_PATH)

        required_columns_station = {'OpID', 'TollID', 'Name', 'PM', 'Locality', 'Road', 'Lat', 'Long', 'Price1', 'Price2', 'Price3', 'Price4'}
        required_columns_operator = {'OpID', 'Operator', 'Email'}

        if not required_columns_station.issubset(df.columns) or not required_columns_operator.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Invalid CSV format"}), 400
 
        if df.isnull().values.any():
            return jsonify({"status": "failed", "info": "CSV contains missing values"}), 400

        db.session.query(TollStation).delete(synchronize_session='fetch')
        db.session.query(TollOperator).delete(synchronize_session='fetch')

        admin_exists = db.session.query(TollOperator).filter_by(OpID='admin').first()
        if admin_exists is None:
            admin_user = TollOperator(
                OpID='ADMIN',
                Name='administrator',
                Email='admin@example.com',
                password='freepasses4all'  
            )
            db.session.add(admin_user)

        operators_added = set()
        for _, row in df.iterrows():
           
            if row['OpID'] not in operators_added:
                new_operator = TollOperator(
                    OpID=row['OpID'],
                    Name=row['Operator'],  
                    Email=row['Email'],
                    password='default_password'  
                )
                db.session.add(new_operator)
                operators_added.add(row['OpID'])

           
            new_station = TollStation(
                TollID=row['TollID'],
                OpID=row['OpID'],
                Name=row['Name'],
                PM=row['PM'],
                Locality=row['Locality'],
                Road=row['Road'],
                Lat=row['Lat'],
                Long=row['Long'],
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


@admin_routes.route('/resetpasses', methods=['POST'])
@token_required
def reset_passes():
    try:
        # Διαγραφή όλων των εγγραφών από Pass, Tag και Debt
        db.session.query(Pass).delete()
        db.session.query(Tag).delete()
        db.session.query(Debt).delete()

        '''
        Θα πρέπει τα passID, DebtID και TagID να ξεκινάει απο την αρχή (1) μετά το reset passes
        '''
        db.session.execute(text('ALTER TABLE pass AUTO_INCREMENT = 1'))
        db.session.execute(text('ALTER TABLE debt AUTO_INCREMENT = 1'))
        db.session.execute(text('ALTER TABLE tag AUTO_INCREMENT = 1'))

        db.session.commit()
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500
    

# Add passes from CSV
@admin_routes.route('/addpasses', methods=['POST'])
@token_required
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

        print("Debugging Passes CSV")
        print(df.head())

        # Έλεγχος για τα απαιτούμενα πεδία
        required_columns = {'timestamp', 'tollID', 'tagRef', 'tagHomeID', 'charge'}
        if not required_columns.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Wrong CSV format"}), 400

        # Έλεγχος για κενά δεδομένα
        if df.isnull().values.any():
            return jsonify({"status": "failed", "info": "CSV contains missing values"}), 400

        # Αφαίρεση duplicate rows από το CSV
        df = df.drop_duplicates()

        # Λήψη των Operators από την βάση
        operators = db.session.query(TollOperator).all()
        operators = [operator.OpID for operator in operators]

        # Αρχικοποίηση του πίνακα debt
        debt_acquired = {operator1: {operator2 : 0 for operator2 in operators} for operator1 in operators}

        # Εισαγωγή δεδομένων στη βάση
        for index, row in df.iterrows():
            # Προσαρμογή για διαφορετικά formats timestamp
            timestamp_str = row['timestamp']
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                except ValueError as e:
                    return jsonify({"status": "failed", "info": str(e)}), 400

            # Έλεγχος αν υπάρχει το tagRef
            existing_tag = Tag.query.filter_by(tagRef=row['tagRef']).first()

            if not existing_tag:
                # Δημιουργία νέου tag αν δεν υπάρχει
                new_tag = Tag(
                    tagRef=row['tagRef'],
                    OpID=row['tagHomeID']
                )
                db.session.add(new_tag)
                db.session.flush()
                tag_id = new_tag.tag_ID
            else:
                # Χρήση υπάρχοντος tag_ID
                tag_id = existing_tag.tag_ID

            # Έλεγχος αν το pass υπάρχει ήδη
            existing_pass = Pass.query.filter(
                and_(
                    Pass.tag_ID == tag_id,
                    Pass.timestamp == timestamp
                )
            ).filter(
                and_(
                    Pass.TollID == row['tollID'],
                    Pass.charge == row['charge']
                )
            ).first()

            if existing_pass:
                continue  # Παράβλεψε την εισαγωγή αν υπάρχει ήδη

            # Δημιουργία νέου pass
            new_pass = Pass(
                tag_ID=tag_id,
                timestamp=timestamp,
                charge=row['charge'],
                TollID=row['tollID']
            )
            print("Inserted pass: ", index)
            # Καθορισμός του operator που ανήκει το tag και του operator του σταθμού
            tag = Tag.query.filter_by(tag_ID=tag_id).first()
            if tag is None:
                # Το tag δεν έχει γίνει ακόμα commit στη βάση οπότε πρέπει να το ψάξουμε στο session
                tag = db.session.query(Tag).filter_by(tag_ID=tag_id).first()
            operator_owing = tag.OpID
            toll_station = TollStation.query.filter_by(TollID=row['tollID']).first()
            if toll_station is None:
                # Πρέπει να κοιτάξουμε στο session για το station
                toll_station = db.session.query(TollStation).filter_by(TollID=row['tollID']).first()
            operator_owed = toll_station.OpID
            # Για τη νέα διέλευση, υπολογισμός του χρέους προς τον operator
            if operator_owing != operator_owed:
                debt_acquired[operator_owing][operator_owed] += row['charge']
            db.session.add(new_pass)

        ''' 
        Πρέπει να υπολογίζεται το χρέος από κάθε operator σε κάθε άλλον και να
        καταχωρείται στον πίνακα Debt
        '''

        # Εισαγωγή των χρεών στον πίνακα debt
        for operator1 in debt_acquired:
            for operator2 in debt_acquired[operator1]:
                if debt_acquired[operator1][operator2] > 0:
                    new_debt = Debt(
                        Operator_ID_1=operator1,
                        Operator_ID_2=operator2,
                        Nominal_Debt=debt_acquired[operator1][operator2],
                        Date=datetime.now().date(),
                        Status='Pending'
                    )
                    db.session.add(new_debt)

        # Commit στη βάση δεδομένων
        db.session.commit()
        return jsonify({"status": "OK"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500