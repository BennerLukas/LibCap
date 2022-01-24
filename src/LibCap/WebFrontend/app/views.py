import logging
from flask import render_template, redirect, abort, send_file, request, session
from app import app
from app.db_connector import DatabaseConnector
from app.backend_functions import Backend

dbc = DatabaseConnector()
# dbc.example_init()

backend = Backend(dbc)

app.secret_key = '5uY4^$u!%lWlAk%3DkM2iL9^!DtJqfyduTc4pyA1uv9JG5ud!Ew@@dsa5'

@app.context_processor
def logging_in():
    return dict(logged_in=session.get('is_logged_in', False),
                user=session.get('username', None))


@app.route('/')  # Home
def index():
    auslastungs_liste = backend.get_auslastung()
    return render_template("/index.html", auslastungs_liste=auslastungs_liste)


@app.route('/dashboard')
def dashboard():
    objects = dbc.get_select('SELECT DISTINCT * FROM objects')
    objects_grouped = list()
    for y in objects.n_grid_coordinate_y.unique():
        objects_grouped.append(objects.loc[objects['n_grid_coordinate_y'] == y].drop('n_grid_coordinate_y', axis=1) \
                               .sort_values(by='n_grid_coordinate_x').to_numpy().tolist())
    logging.error(objects.info())
    logging.error(objects_grouped)
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
                  "LAN": request.form['gridCheck1'],
                  "Lampe": request.form['gridCheck2'],
                  "Steckdose": request.form['gridCheck3'],
                  "Drehstuhl": request.form['gridCheck4']}
    new_id = backend.add_controller_to_database(param_list)
    return redirect("/add_controller")
