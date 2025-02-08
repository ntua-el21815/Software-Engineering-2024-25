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
        if cur_user.authenticate(password) == 1:
            flash(f'Welcome {cur_user.opname}!')
            session['user'] = cur_user.to_dict()
            session['data'] = {}
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
    cur_user = User(session['user'])

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
            return redirect(url_for('payments'))
        if start_date > end_date:
            flash("Start date cannot be greater than end date")
            return redirect(url_for('payments'))
        
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
            'start_date': start_date,
            'end_date': end_date,
        }
        return render_template('payments.html', css_file='payments.css', js_file='payments.js', data=debt_data)
    return render_template('payments.html', css_file='payments.css', js_file='payments.js', data=session['data'].get('debt_data', []))

@app.route('/map', methods=['GET', 'POST'])
def map():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
        start_date = request.form.get('start-date')
        end_date = request.form.get('end-date')

        if not start_date or not end_date:
            flash("Please select a date range")
            return redirect(url_for('map'))

        if start_date > end_date:
            flash("Start date cannot be greater than end date")
            return redirect(url_for('map'))

        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')

        # ... Here calcStats function should be called and we'll get the data from the API

    cur_user = User(session['user'])
    stations = cur_user.getStations()
    station_list = []
    op_names = getOpNames()
    for station in stations["stationList"]:
        station_list.append({
            "stationID": station["stationID"],
            "stationName": station["stationName"],
            "stationOperator": op_names[station["stationOperator"]].capitalize(),
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
    comp_stations = json.dumps([station for station in station_list if station["stationOperator"] == op_names[cur_user.opid].capitalize()])
    otr_stations = json.dumps([station for station in station_list if station["stationOperator"] != op_names[cur_user.opid].capitalize()])
    if stations == -1:
        flash("Error fetching data from the API")
        return render_template('map.html', css_file='map.css')
    return render_template('map.html', css_file='map.css', js_file='map.js', station_list=station_list_json,company_stations=comp_stations,other_stations=otr_stations, admin=False)

@app.route('/make_payment', methods=['POST'])
def make_payment():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
            cur_user = User(session['user'])
            data = request.get_json()
            operators = data.get('operators', [])
            operators = [op.strip() for op in operators]
            print(operators)
            operator_ids = []
            op_names = getOpNames()
            print(op_names)
            for key, value in op_names.items():
                if value in operators:
                    operator_ids.append(key)
            print(operator_ids)
            start_date = session['data'].get('start_date', None)
            end_date = session['data'].get('end_date', None)

            if not operator_ids or not start_date or not end_date:
                flash("You haven't selected any operators or dates")
                return ('Bad Request: Missing operators or dates', 400)
            
            # Make the payment and collect all debts
            all_debt_list = []
            for operator in operator_ids:
                payment_response = cur_user.makePayment(operator, start_date, end_date)
                if payment_response.status_code != 200:
                    flash(f"Error making payment to {op_names[operator]}: {payment_response.text}")
                    return render_template('payments.html', css_file='payments.css', js_file='payments.js', data=session['data'].get('debt_data', [])), 500
                response_json = payment_response.json()
                debt_list = response_json.get('debtList', [])
                all_debt_list.extend(debt_list)
            
            # Prepare data for CSV file
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)

            total_amount = sum(item['Debt_Amount'] for item in session['data'].get('debt_data', []) if item['Operator'] in operators)
            payment_time_str = datetime.now().strftime("%d/%m/%Y %H:%M")

            csv_writer.writerow(["Time of Payment", "Total Amount Paid"])
            csv_writer.writerow([
                payment_time_str,
                round(total_amount, 2)
            ])
            csv_writer.writerow([])
            csv_writer.writerow(["Operator Paid", "Date Incurred", "Amount", "Date Paid"])

            for debt in all_debt_list:
                csv_writer.writerow([
                op_names[debt['Operator_ID_2']],
                debt['Date'],
                debt['Nominal_Debt'],
                payment_time_str
                ])

            csv_data.seek(0)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"payment_details_{current_time}.csv"
            response = app.response_class(
                csv_data.getvalue(),
                mimetype='text/csv',
                headers={"Content-Disposition": f"attachment;filename={filename}"}
            )
            session['data'] = {}
            return response


if __name__ == '__main__':
    # Τοποθεσία του αρχείου της τρέχουσας εφαρμογής
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # Τοποθεσία του αρχείου του SSL certificate
    context = (this_dir + '/ssl/server.crt', this_dir + '/ssl/server.key')
    ip = socket.gethostbyname(socket.gethostname())
    app.run(host=ip, port=443, ssl_context=context, debug=True)

