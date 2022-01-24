import datetime
import logging
import werkzeug
from flask import render_template, redirect, abort, send_file, request, session, flash
from app import app
from app.db_connector import DatabaseConnector
from app.backend_functions import Backend

dbc = DatabaseConnector()
# dbc.example_init()
backend = Backend(dbc)


@app.route('/')  # Home
def index():
    occupancy_rate = backend.get_auslastung()
    ctr_occupied_workstations = 1
    ctr_available_workstations = 1
    ctr_maintenance_workstations = 1
    ctr_total_workstations = 1
    return render_template("/index.html",
                           auslastungs_liste=occupancy_rate,
                           ctr_occupied_workstations=ctr_occupied_workstations,
                           ctr_available_workstations=ctr_available_workstations,
                           ctr_maintenance_workstations=ctr_maintenance_workstations,
                           ctr_total_workstations=ctr_total_workstations,
                           )


@app.route('/dashboard')
def dashboard():
    objects_grouped = backend.get_sitzplaetze()
    return render_template("/dashboard.html", objects=objects_grouped)


@app.route('/reservierung')
def reservierung():
    active_user_name = session.get('username', None)
    if active_user_name is not None:
        reservations = dbc.get_select(f'SELECT * FROM reservations WHERE username = {active_user_name}')
        return render_template("/reservierungen.html", zip=zip, column_names=list(reservations.columns.values),
                               row_data=list(reservations.values.tolist()), is_logged_in=session.get('is_logged_in'))
    else:
        return render_template("/reservierungen.html", zip=zip, column_names=list(),
                               row_data=list(), is_logged_in=session.get('is_logged_in'))


@app.route("/add_controller", methods=['POST', 'GET'])
def add_controller():
    active_user_name = session.get("username", None)
    return render_template("/add_controller.html")


@app.route('/add_examples')
def add_examples():
    pass
    # dbc.example_init()
    # return redirect("/", code=303)


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template("login.html")


@app.route('/logged_in', methods=['POST', 'GET'])
def logged_in():
    session['is_logged_in'] = backend.set_user(request.form['username'], request.form['password'])
    if session.get('is_logged_in') is False:
        return render_template("includes/fail.html", title='Failed Log-In',
                               text='You have not been logged in.')
    else:
        session['username'] = request.form['username']
        return render_template("includes/success.html", title='Successful Login',
                               text='You have been successfully logged in.')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session['logged_in'] = False
    session['username'] = None
    backend.s_user = None
    return render_template("includes/success.html", title='Successful Logout',
                           text='You have been successfully logged out.')


@app.route('/execute_add_controller', methods=['POST', 'GET'])
def execute_add_controller():

    param_list = {"x": request.form['inputX'],
                  "y": request.form['inputY'],
                  "z": request.form['inputZ'],
                  "status": request.form['gridRadios'],
                  "LAN": request.form.get('gridCheck1', "off"),
                  "Lampe": request.form.get('gridCheck2', "off"),
                  "Steckdose": request.form.get('gridCheck3', "off"),
                  "Drehstuhl": request.form.get('gridCheck4', "off")}
    new_id = backend.add_controller_to_database(param_list)
    flash(f"Neuer Controller mit ID {new_id} hinzugefügt!")
    return redirect("/add_controller")


@app.post('/reserve_seat')
def reserve_seat():
    seat_id = request.form.get('seat_id')
    time_formatted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_string = f"UPDATE OBJECTS SET n_status_id = 5, ts_last_change='{time_formatted}' WHERE n_object_id={seat_id}"
    dbc.execute_sql(sql_string)
    logging.info(f"Reserved {seat_id} until {time_formatted}")
    return redirect("/dashboard")
