from flask import render_template
from app import app
import app.db_connector as dbc


@app.route('/')  # Home
def index():
    return render_template("/index.html")
