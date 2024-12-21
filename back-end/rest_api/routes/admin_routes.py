from flask import Blueprint, jsonify
from models import db, Pass, Tag, TollOperator, TollStation
from flask import request
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/healthcheck', methods=['GET'])
def healthcheck():
    try:
        # Ελέγχει τη σύνδεση με τη βάση δεδομένων
        db.session.execute(text('SELECT 1'))  # Χρήση του text για SQLAlchemy 2.x

        # Συλλογή δεδομένων για απάντηση
        n_stations = db.session.query(TollStation).count()  # Αριθμός σταθμών
        n_tags = db.session.query(Tag).count()  # Αριθμός tags
        n_passes = db.session.query(Pass).count()  # Αριθμός passes

        # Δημιουργία connection string (προσαρμοσμένο για την περίπτωσή σου)
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
        required_columns_station = {'OpID', 'TollID', 'Name', 'PM', 'Locality', 'Road', 'Lat', 'Long', 'Price1', 'Price2', 'Price3', 'Price4'}
        required_columns_operator = {'OpID', 'Operator', 'Email'}

        if not required_columns_station.issubset(df.columns) or not required_columns_operator.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Invalid CSV format"}), 400
        
        # Έλεγχος για κενές τιμές
        if df.isnull().values.any():
            return jsonify({"status": "failed", "info": "CSV contains missing values"}), 400

        # Διαγραφή όλων των εγγραφών στους πίνακες Toll_Station και Toll_Operator
        db.session.query(TollStation).delete(synchronize_session='fetch')
        db.session.query(TollOperator).delete(synchronize_session='fetch')

        # Εισαγωγή νέων δεδομένων από το CSV στους πίνακες Toll_Station και Toll_Operator
        operators_added = set()
        for _, row in df.iterrows():
            # Αρχικοποίηση TollOperator (αν δεν έχει ήδη εισαχθεί)
            if row['OpID'] not in operators_added:
                new_operator = TollOperator(
                    OpID=row['OpID'],
                    Name=row['Operator'],  # Operator στο CSV αντιστοιχεί στο Name στον πίνακα
                    Email=row['Email'],
                    password='default_password'  # Προσθήκη προεπιλεγμένου password
                )
                db.session.add(new_operator)
                operators_added.add(row['OpID'])

            # Αρχικοποίηση TollStation
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

        # Commit στη βάση δεδομένων
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

        '''
        Θα πρέπει το passID να ξεκινάει απο την αρχή (1) μετά το reset passes
        '''
        db.session.execute(text('ALTER TABLE pass AUTO_INCREMENT = 1'))

        # Προαιρετική δημιουργία διαχειριστικού λογαριασμού
        admin_exists = db.session.query(TollOperator).filter_by(OpID='admin').first()
        if not admin_exists:
            admin_user = TollOperator(
                OpID='admin',
                Name='Administrator',
                Email='admin@example.com',
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

        # Έλεγχος για τα απαιτούμενα πεδία
        required_columns = {'timestamp', 'tollID', 'tagRef', 'tagHomeID', 'charge'}
        if not required_columns.issubset(df.columns):
            return jsonify({"status": "failed", "info": "Wrong CSV format"}), 400

        # Έλεγχος για κενά δεδομένα
        if df.isnull().values.any():
            return jsonify({"status": "failed", "info": "CSV contains missing values"}), 400

        # Αφαίρεση duplicate rows από το CSV
        df = df.drop_duplicates()

        # Εισαγωγή δεδομένων στη βάση
        for _, row in df.iterrows():
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
                db.session.flush()  # Δημιουργία του `tag_ID` για το foreign key

                tag_id = new_tag.tag_ID
            else:
                # Χρήση υπάρχοντος tag_ID
                tag_id = existing_tag.tag_ID

            # Έλεγχος αν το pass υπάρχει ήδη
            existing_pass = Pass.query.filter(
                and_(
                    Pass.tag_ID == tag_id,
                    Pass.timestamp == timestamp,
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
            db.session.add(new_pass)

        # Commit στη βάση δεδομένων
        db.session.commit()
        return jsonify({"status": "OK"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500