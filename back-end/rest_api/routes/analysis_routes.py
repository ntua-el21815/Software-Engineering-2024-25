from flask import Blueprint, jsonify
from datetime import datetime
from models import Pass, Tag, TollStation, TollOperator, Debt, Settlement
from sqlalchemy import func
from models import db
from sqlalchemy import and_

analysis_routes = Blueprint('analysis_routes', __name__)

@analysis_routes.route('/getTollStations', methods=['GET'])
def get_toll_stations():
    try:
        # Επιστροφή όλων των σταθμών
        stations = TollStation.query.all()

        # Δημιουργία λίστας με τους σταθμούς
        station_list = []
        for station in stations:
            station_list.append({
            "stationID": station.TollID,
            "stationName": station.Name,
            "stationOperator": station.OpID,
            "Latitude": station.Lat,
            "Longitude": station.Long,
            "PM": station.PM,
            "Price1": station.Price1,
            "Price2": station.Price2,
            "Price3": station.Price3,
            "Price4": station.Price4
            })

        # Δημιουργία του τελικοϋ JSON αντικειμένου
        response = {
            "nStations": len(station_list),
            "stationList": station_list
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

@analysis_routes.route('/getOpNames', methods=['GET'])
def get_op_names():
    try:
        # Επιστροφή όλων των τελεστών
        operators = TollOperator.query.all()
        # Δημιουργία λίστας με τους τελεστές
        response = {}
        for operator in operators:
            response[operator.OpID] = operator.Name
        print(response)
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

@analysis_routes.route('/tollStationPasses/<tollStationID>/<date_from>/<date_to>', methods=['GET'])
def toll_station_passes(tollStationID, date_from, date_to):
    try:
        print("Database instance:", db)
        # Μετατροπή των ημερομηνιών σε datetime αντικείμενα
        date_from_dt = datetime.strptime(date_from, "%Y%m%d")
        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        # Ανάκτηση του σταθμού
        station = TollStation.query.filter_by(TollID=tollStationID).first()
        if not station:
            return jsonify({"status": "failed", "info": f"TollStationID {tollStationID} not found"}), 404

        # Ανάκτηση των διελεύσεων για τον σταθμό και την περίοδο
        passes = db.session.query(Pass, Tag).join(Tag, Pass.tag_ID == Tag.tag_ID).filter(
            Pass.TollID == tollStationID,
            Pass.timestamp >= date_from_dt,
            Pass.timestamp <= date_to_dt
        ).order_by(Pass.timestamp).all()

        # Δημιουργία λίστας με διελεύσεις
        pass_list = []
        for idx, (p, t) in enumerate(passes):
            # Προσδιορισμός του passType
            pass_type = "home" if t.OpID == station.OpID else "visitor"

            pass_list.append({
                "passIndex": idx + 1,
                "passID": p.passID,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M"),
                "tagID": t.tag_ID,
                "tagProvider": t.OpID,
                "passType": pass_type,
                "passCharge": p.charge
            })

        # Δημιουργία του τελικού αντικειμένου JSON
        response = {
            "stationID": tollStationID,
            "stationOperator": station.OpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": len(pass_list),
            "passList": pass_list
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

@analysis_routes.route('/passAnalysis/<stationOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
def pass_analysis(stationOpID, tagOpID, date_from, date_to):
    try:
        # Μετατροπή των ημερομηνιών σε datetime αντικείμενα
        date_from_dt = datetime.strptime(date_from, "%Y%m%d")
        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        # Ανάκτηση των σταθμών που ανήκουν στον stationOpID
        station_ids = TollStation.query.with_entities(TollStation.TollID).filter(
            TollStation.OpID == stationOpID
        ).all()

        station_ids = [sid[0] for sid in station_ids]  # Λίστα με IDs των σταθμών

        # Ανάκτηση των διελεύσεων που ανήκουν στον tagOpID και σχετίζονται με τους σταθμούς του stationOpID
        passes = db.session.query(Pass, Tag).join(Tag, Pass.tag_ID == Tag.tag_ID).filter(
            Tag.OpID == tagOpID,
            Pass.TollID.in_(station_ids),
            Pass.timestamp >= date_from_dt,
            Pass.timestamp <= date_to_dt
        ).order_by(Pass.timestamp).all()

        # Δημιουργία λίστας με διελεύσεις
        pass_list = []
        for idx, (p, t) in enumerate(passes):
            pass_list.append({
                "passIndex": idx + 1,
                "passID": p.passID,
                "stationID": p.TollID,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "tagID": t.tag_ID,
                "passCharge": p.charge
            })

        # Δημιουργία του τελικού αντικειμένου JSON
        response = {
            "stationOpID": stationOpID,
            "tagOpID": tagOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": len(pass_list),
            "passList": pass_list
        }

        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

    
@analysis_routes.route('/passesCost/<tollOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
def passes_cost(tollOpID, tagOpID, date_from, date_to):
    try:
        # Μετατροπή των ημερομηνιών σε datetime αντικείμενα
        date_from_dt = datetime.strptime(date_from, "%Y%m%d")
        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        # Εύρεση των σταθμών που ανήκουν στον tollOpID
        station_ids = TollStation.query.with_entities(TollStation.TollID).filter(
            TollStation.OpID == tollOpID
        ).all()
        station_ids = [sid[0] for sid in station_ids]  # Λίστα με IDs των σταθμών

        # Υπολογισμός αριθμού διελεύσεων και συνολικού κόστους για τα tags του tagOpID
        result = db.session.query(
            func.count(Pass.passID).label("nPasses"),
            func.sum(Pass.charge).label("passesCost")
        ).join(Tag, Pass.tag_ID == Tag.tag_ID).filter(
            Tag.OpID == tagOpID,
            Pass.TollID.in_(station_ids),
            Pass.timestamp >= date_from_dt,
            Pass.timestamp <= date_to_dt
        ).first()
        print("Result:", result)
        
        # Ανάκτηση των αποτελεσμάτων
        n_passes = result.nPasses or 0
        passes_cost = float(result.passesCost or 0.0)

        # Δημιουργία του τελικού JSON αντικειμένου
        response = {
            "tollOpID": tollOpID,
            "tagOpID": tagOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": n_passes,
            "passesCost": passes_cost
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500
    
@analysis_routes.route('/chargesBy/<tollOpID>/<date_from>/<date_to>', methods=['GET'])
def charges_by(tollOpID, date_from, date_to):
    try:
        # Μετατροπή των ημερομηνιών σε datetime αντικείμενα
        date_from_dt = datetime.strptime(date_from, "%Y%m%d")
        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        # Εντοπισμός των σταθμών που ανήκουν στον tollOpID
        station_ids = db.session.query(TollStation.TollID).filter(
            TollStation.OpID == tollOpID
        ).subquery()

        # Υπολογισμός των διελεύσεων και του κόστους ανά visiting operator
        results = db.session.query(
            Tag.OpID.label("visitingOpID"),
            func.count(Pass.passID).label("nPasses"),
            func.sum(Pass.charge).label("passesCost")
        ).join(Tag, Pass.tag_ID == Tag.tag_ID).filter(
            Pass.TollID.in_(station_ids),
            Pass.timestamp >= date_from_dt,
            Pass.timestamp <= date_to_dt
        ).group_by(Tag.OpID).all()

        # Διαμόρφωση της λίστας visiting operators (vOpList)
        vOpList = [
            {
                "visitingOpID": row.visitingOpID,
                "nPasses": row.nPasses,
                "passesCost": float(row.passesCost or 0.0)
            }
            for row in results
        ]

        # Δημιουργία του τελικού JSON αντικειμένου
        response = {
            "tollOpID": tollOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "vOpList": vOpList
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500

@analysis_routes.route('/owedBy/<OpID>/<date_from>/<date_to>', methods=['GET'])
def owed_by(OpID, date_from, date_to):
    try:
        # Validate date format
        try:
            date_from = datetime.strptime(date_from, "%Y%m%d").date()
            date_to = datetime.strptime(date_to, "%Y%m%d").date()
        except ValueError:
            return jsonify({"status": "failed", "info": "Invalid date format"}), 400

        # Query the Debt table to calculate the total amount owed by the operator
        debts = db.session.query(Debt).filter(
            and_(
                Debt.Operator_ID_1 ==  OpID,
                Debt.Date >= date_from,
                Debt.Date <= date_to
            )
        ).all()

        # Calculate the total amount owed to each operator

        owed_to = {}
        for debt in debts:
            if debt.Operator_ID_2 not in owed_to:
                owed_to[debt.Operator_ID_2] = 0
            owed_to[debt.Operator_ID_2] += debt.Nominal_Debt

        # Rounding the amounts to two decimal places
        owed_to = {k: round(v, 2) for k, v in owed_to.items()}

        # Create the final JSON object
        response = {
            "OpID": OpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from.strftime("%Y-%m-%d"),
            "periodTo": date_to.strftime("%Y-%m-%d"),
            "owedTo": owed_to
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500
    
@analysis_routes.route('makePayment/<FromOpID>/<ToOpID>/<date_from>/<date_to>', methods=['POST'])
def make_payment(FromOpID, ToOpID, date_from, date_to):
    try:
        # Validate date format
        try:
            date_from = datetime.strptime(date_from, "%Y%m%d").date()
            date_to = datetime.strptime(date_to, "%Y%m%d").date()
        except ValueError:
            return jsonify({"status": "failed", "info": "Invalid date format"}), 400

        # Query the Debt table to find all pending debts
        debts = db.session.query(Debt).filter(
            and_(
                Debt.Operator_ID_1 == FromOpID,
                Debt.Operator_ID_2 == ToOpID,
                Debt.Date >= date_from,
                Debt.Date <= date_to,
                Debt.Status == "Pending"
            )
        ).all()

        # Calculate the total amount to be paid
        total_amount = sum(debt.Nominal_Debt for debt in debts)

        # Update the status of the debts to "Paid"
        for debt in debts:
            debt.Status = "Paid"

        # Create a new settlement entry
        settlement = Settlement(
            Operator_ID_1=FromOpID,
            Operator_ID_2=ToOpID,
            Amount=total_amount,
            Date=datetime.now().date()
        )
        db.session.add(settlement)

        # Commit the changes to the database
        db.session.commit()

        # Create the final JSON object
        response = {
            "FromOpID": FromOpID,
            "ToOpID": ToOpID,
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from.strftime("%Y-%m-%d"),
            "periodTo": date_to.strftime("%Y-%m-%d"),
            "totalAmountPaid": round(total_amount, 2)
        }

        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "failed", "info": str(e)}), 500