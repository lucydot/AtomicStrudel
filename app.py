from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


class MP_ID(FlaskForm):
    mp_id = StringField(
        "What is the Materials Project ID?", validators=[DataRequired()]
    )
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        # Safely retrieve data using the HTML name attribute
        username = request.form.get("user_input")
        return render_template("index_updated.html")

    colours = ["Red", "Blue", "Black", "Orange"]
    return render_template("index.html", colours=colours)
