import datetime
import logging
import werkzeug
from flask import render_template, redirect, abort, send_file, request, session, flash
from app import app
from app.db_connector import DatabaseConnector
from app.backend_functions import Backend

dbc = DatabaseConnector()
dbc.example_init()
backend = Backend(dbc)
app.secret_key = '5uY4^$u!%lWlAk%3DkM2iL9^!DtJqfyduTc4pyA1uv9JG5ud!Ew@@dsa5'


@app.route('/')  # Home
def index():
    occupancy_rate = backend.get_auslastung()
    ctr_occupied_workstations, ctr_available_workstations, ctr_maintenance_workstations, ctr_total_workstations = backend.get_counter()
    objects_grouped = backend.get_sitzplaetze()
    return render_template("/index.html",
                           auslastungs_liste=occupancy_rate,
                           ctr_occupied_workstations=ctr_occupied_workstations,
                           ctr_available_workstations=ctr_available_workstations,
                           ctr_maintenance_workstations=ctr_maintenance_workstations,
                           ctr_total_workstations=ctr_total_workstations,
                           objects=objects_grouped
                           )


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
    flash(f"Neuer Controller mit ID {new_id} hinzugefügt!")
    return redirect("/")


@app.post('/reserve_seat')
def reserve_seat():
    seat_id = request.form.get('seat_id')
    time_formatted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql_string = f"UPDATE OBJECTS SET n_status_id = 5, ts_last_change='{time_formatted}' WHERE n_object_id={seat_id}"
    dbc.execute_sql(sql_string)
    logging.info(f"Reserved {seat_id} until {time_formatted}")
    return redirect("/")
