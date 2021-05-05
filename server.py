from flask import Flask, render_template, redirect, flash, session, request
import jinja2
import os

FLASK_KEY = os.environ["FLASK_KEY"]

app = Flask(__name__)

app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.secret_key = FLASK_KEY

@app.route("/")
def index():
    
    return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')