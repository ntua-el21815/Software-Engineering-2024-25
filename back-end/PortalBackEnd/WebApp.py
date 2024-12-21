from flask import Flask, render_template, request, redirect, url_for, flash, session
from APIWrapper import User
from datetime import datetime
import json
import csv
import io

app = Flask(
    __name__,
    template_folder="../../front-end/templates",  # Path to templates
    static_folder="../../front-end/static"  # Path to static files (CSS, JS, images, etc.)
)
app.secret_key = "temporary_secret"
session = {}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur_user = User(username)
        if cur_user.authenticate(password) > 0:
            flash(f'Welcome {username}')
            session['user'] = cur_user.to_dict()
            session['data'] = []
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
        
        print(session['user']) # Debugging purposes
        cur_user = User(session['user']['username'])
        cur_user.from_dict(session['user'])

        # Handle date filter request 
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
      
        if start_date is None or end_date is None:
            flash("Please select a date range")
            return render_template('dashboard.html', data=session['data'])
        if start_date > end_date:
            flash("Start date cannot be greater than end date")
            return render_template('dashboard.html', data=session['data'])
        
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        
        # Get the data from the API
        debt_data = cur_user.calcCharges(start_date, end_date)
        if debt_data == -1:
            flash("Error fetching data from the API")
            return render_template('dashboard.html', data=[])
        debt_data = debt_data["vOpList"]
        debt_data = [{"Operator": item["visitingOpID"], "Debt_Amount": item["passesCost"]} for item in debt_data]

        start_date_formatted = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
        end_date_formatted = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
        flash(f"Filtering data from {start_date_formatted} to {end_date_formatted}")
        session['data'] = debt_data
        return render_template('dashboard.html', data=debt_data)
    return render_template('dashboard.html', data=[])

@app.route('/make_payment', methods=['POST'])
def make_payment():
    if 'user' not in session:
        flash("Please login first")
        return redirect(url_for('login'))
    if request.method == 'POST':
            flash("Payment successful")
            payment_summary = json.dumps(session['data'])
            response = app.response_class(
                response=payment_summary,
                status=200,
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = 'attachment; filename=payment_summary.json'
            # Convert session['data'] to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Operator', 'Payment in Euros'])
            for item in session['data']:
                writer.writerow([item['Operator'], item['Debt_Amount']])
            response = app.response_class(
                response=output.getvalue(),
                status=200,
                mimetype='text/csv'
            )
            current_date = datetime.now().strftime('%Y%m%d')
            response.headers['Content-Disposition'] = f'attachment; filename=payment_summary_{current_date}.csv'
            return response
    return render_template('dashboard.html', data=[])
if __name__ == '__main__':
    app.run(debug=True)

