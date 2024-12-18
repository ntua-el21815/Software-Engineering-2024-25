from flask import Blueprint, jsonify, request
from datetime import datetime
from models import Pass, TollStation, TollOperator, Tag
from sqlalchemy import func

pass_routes = Blueprint('pass_routes', __name__)

@pass_routes.route('/tollStationPasses/<station_id>/<date_from>/<date_to>', methods=['GET'])
def get_passes(station_id, date_from, date_to):
    try:
        # Μετατροπή ημερομηνιών σε datetime αντικείμενα
        date_from_dt = datetime.strptime(date_from, "%Y%m%d")
        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        # Ανάκτηση του σταθμού και του operator
        station = TollStation.query.filter_by(Toll_Station_ID=station_id).first()
        if not station:
            return jsonify({"status": "failed", "info": "Station not found"}), 404

        operator = TollOperator.query.filter_by(Operator_ID=station.Toll_OperatorOperator_ID).first()

        # Ανάκτηση των διελεύσεων και σχετικών tags
        passes = db.session.query(Pass, Tag).join(Tag, Pass.tag_ID == Tag.tag_ID).filter(
            Pass.Toll_Station_ID == station_id,
            Pass.timestamp >= date_from_dt,
            Pass.timestamp <= date_to_dt
        ).order_by(Pass.timestamp).all()

        # Δημιουργία λίστας διελεύσεων με το passType
        pass_list = []
        for idx, (p, t) in enumerate(passes):
            pass_type = "home" if t.tagHomeID == station.Toll_OperatorOperator_ID else "visitor"

            pass_list.append({
                "passIndex": idx + 1,
                "passID": p.passID,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "tagID": t.tag_ID,
                "tagProvider": t.tagHomeID,
                "passType": pass_type,
                "passCharge": p.charge
            })

        # Δημιουργία τελικού JSON αντικειμένου
        response = {
            "stationID": station_id,
            "stationOperator": operator.Name if operator else "Unknown",
            "requestTimestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "periodFrom": date_from,
            "periodTo": date_to,
            "nPasses": len(pass_list),
            "passList": pass_list
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 500
