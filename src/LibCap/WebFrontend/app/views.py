import datetime
import logging
import werkzeug
from flask import render_template, redirect, abort, send_file, request, session, flash, url_for
from app import app
from app.db_connector import DatabaseConnector
from app.backend_functions import Backend

dbc = DatabaseConnector()
dbc.example_init()
backend = Backend(dbc)
app.secret_key = '5uY4^$u!%lWlAk%3DkM2iL9^!DtJqfyduTc4pyA1uv9JG5ud!Ew@@dsa5'


@app.route('/')  # Home
def index():
    # 14 total
    # 10 freie
    # 4 belegt
    #
    occupancy_rate = backend.get_occupancy()
    ctr_occupied_workstations, ctr_available_workstations, ctr_maintenance_workstations, ctr_total_workstations = backend.get_counter()
    objects_grouped = backend.get_dashboard_infos()
    workstations = backend.get_workstations()
    current_usage = round(((ctr_occupied_workstations + ctr_maintenance_workstations) / ctr_total_workstations) * 100, 1)
    timeseries_forecast = backend.get_timeseries_forecast()
    return render_template("/index.html",
                           auslastungs_liste=occupancy_rate,
                           ctr_occupied_workstations=ctr_occupied_workstations,
                           ctr_available_workstations=ctr_available_workstations,
                           ctr_maintenance_workstations=ctr_maintenance_workstations,
                           ctr_total_workstations=ctr_total_workstations,
                           objects=objects_grouped,
                           workstations=workstations,
                           current_usage=current_usage,
                           timeseries_forecast=timeseries_forecast
                           )


@app.post('/refresh_dashboard')
def refresh_dashboard():
    return redirect(url_for('index') + '#dashboard')


@app.post('/execute_add_controller')
def execute_add_controller():
    param_list = {"x": request.form['inputX'],
                  "y": request.form['inputY'],
                  "status": request.form['gridRadios'],
                  "Ethernet": request.form.get('gridCheck1', "off"),
                  "Lamp": request.form.get('gridCheck2', "off"),
                  "Plug": request.form.get('gridCheck3', "off"),
                  "PC": request.form.get('gridCheck4', "off")}
    new_id = backend.add_controller_to_database(param_list)
    if new_id is None:
        flash(f"No controller added. Place already used!")
    else:
        flash(f"New controller with id {new_id[0][0]} added!")
    return redirect(url_for('index') + '#add')


@app.post('/reserve_seat')
def reserve_seat():
    seat_id = request.form.get('seat_id')
    time_formatted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_string = f"UPDATE OBJECTS SET n_status_id = 5, ts_last_change='{time_formatted}' WHERE n_object_id={seat_id}"
    dbc.execute_sql(sql_string)
    logging.info(f"Reserved {seat_id} until {time_formatted}")
    return redirect(url_for('index') + '#dashboard')


@app.post('/manage_controller')
def manage_controller():
    print(request.form)
    if request.form.get("button") == "update_status":
        backend.update_status(request.form.get("workstation"), request.form.get("state"))
    elif request.form.get("button") == "update_equipment":
        equipment = {
                      "Ethernet": request.form.get('ethernet', "off"),
                      "Lamp": request.form.get('lamp', "off"),
                      "Plug": request.form.get('plug', "off"),
                      "PC": request.form.get('pc', "off")
        }
        backend.update_equipment(request.form.get("workstation"), equipment)
    elif request.form.get("button") == "delete":
        backend.delete(request.form.get("workstation"))

    return redirect(url_for('index') + '#manage')
