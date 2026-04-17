from flask import render_template
from flask_app import app

@app.route("/")
def overlay():
    return render_template("index.html")

@app.route("/config")
def config_page():
    return render_template("config.html")