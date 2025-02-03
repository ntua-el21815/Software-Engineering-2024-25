from flask import Flask, render_template, request, redirect, url_for, flash, session
from api_wrapper import User, getOpNames
from datetime import datetime
import json
import csv
import io
import os
import socket

app = Flask(
    __name__,
    template_folder="../../front-end/templates",  # Path to templates
    static_folder="../../front-end/static"  # Path to static files (CSS, JS, images, etc.)
)
app.secret_key = "temporary_secret"


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    session['data'] = {}
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur_user = User(username)
        if cur_user.authenticate(password) > 0:
            flash(f'Welcome {cur_user.opname}!')
            session['user'] = cur_user.to_dict()
            session['data'] = []
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
        return render_template('login.html', css_file='login.css')
    return render_template('login.html', css_file='login.css')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    session['data'] = {}
    return render_template('dashboard.html')


@app.route('/payments', methods=['GET', 'POST'])
def payments():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    print(session['user']) # Debugging purposes
    cur_user = User(session['user']['username'])
    cur_user.from_dict(session['user'])

    if cur_user.opid == "ADMIN":
        flash("Payments are not available for admin users")
        return render_template('dashboard.html', data=session['data'])
    
    if request.method == 'POST':

        # Handle date filter request 
        start_date = request.args.get('start-date') or request.form.get('start-date')
        end_date = request.args.get('end-date') or request.form.get('end-date')

        print(start_date, end_date) # Debugging purposes
      
        if start_date is None or end_date is None:
            flash("Please select a date range")
            return render_template('dashboard.html', data=session['data'])
        if start_date > end_date:
            flash("Start date cannot be greater than end date")
            return render_template('dashboard.html', data=session['data'])
        
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        
        # Get the data from the API
        debts = cur_user.calcCharges(start_date, end_date)
        if debts == -1:
            flash("Error fetching data from the API")
            return render_template('dashboard.html', data=[])
        op_names = getOpNames()
        debt_data = [{'Operator': op_names[op], 'Debt_Amount': debts[op]} for op in debts if debts[op] > 0]
        start_date_formatted = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
        end_date_formatted = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
        flash(f"Filtering data from {start_date_formatted} to {end_date_formatted}")
        session['data'] = {
            'debt_data': debt_data,
            'start_date': start_date_formatted,
            'end_date': end_date_formatted
        }
        return render_template('payments.html', css_file='payments.css', js_file='payments.js', data=debt_data)
    return render_template('payments.html', css_file='payments.css', js_file='payments.js', data=session['data'].get('debt_data', []))

@app.route('/map', methods=['GET', 'POST'])
def map():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    cur_user = User(session['user']['username'])
    cur_user.from_dict(session['user'])
    stations = cur_user.getStations()
    station_list = []
    for station in stations["stationList"]:
        station_list.append({
            "stationID": station["stationID"],
            "stationName": station["stationName"],
            "stationOperator": station["stationOperator"],
            "Latitude": station["Latitude"],
            "Longitude": station["Longitude"],
            "PM": station["PM"],
            "Price1": station["Price1"],
            "Price2": station["Price2"],
            "Price3": station["Price3"],
            "Price4": station["Price4"]
        })
    if cur_user.opid == "ADMIN":
        station_list_json = json.dumps(station_list)
        return render_template('map.html', css_file='map.css', js_file='map.js', station_list=station_list_json, admin=True)
    station_list_json = json.dumps(station_list)
    comp_stations = json.dumps([station for station in station_list if station["stationOperator"] == cur_user.opid])
    otr_stations = json.dumps([station for station in station_list if station["stationOperator"] != cur_user.opid])
    if stations == -1:
        flash("Error fetching data from the API")
        return render_template('map.html', css_file='map.css')
    return render_template('map.html', css_file='map.css', js_file='map.js', station_list=station_list_json,company_stations=comp_stations,other_stations=otr_stations, admin=False)

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    return render_template('statistics.html', css_file='statistics.css')

@app.route('/make_payment', methods=['POST'])
def make_payment():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
            data = request.get_json()
            operators = data.get('operators', [])
            operators = [op.strip() for op in operators]
            start_date = session['data'].get('start_date', None)
            end_date = session['data'].get('end_date', None)

            if not operators or not start_date or not end_date:
                return app.response_class(
                response=json.dumps({"error": "Invalid input"}),
                status=400,
                mimetype='application/json'
                )
            
            # Create CSV file in memory
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Operator', 'Start Date', 'End Date', 'Debt Amount'])

            for item in session['data'].get('debt_data', []):
                if item['Operator'] in operators:
                    writer.writerow([item['Operator'], start_date, end_date, item['Debt_Amount']])

            output.seek(0)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"payment_summary_{current_time}.csv"
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )
            session['data'] = {}
            return response
    return render_template('dashboard.html', data=[])
if __name__ == '__main__':
    # Τοποθεσία του αρχείου της τρέχουσας εφαρμογής
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # Τοποθεσία του αρχείου του SSL certificate
    context = (this_dir + '/ssl/server.crt', this_dir + '/ssl/server.key')
    ip = socket.gethostbyname(socket.gethostname())
    print(f"Server running on https://{ip}:9115")
    app.run(host=ip, port=443, ssl_context=context, debug=True)

