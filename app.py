import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from singingmaterials.dos_stats import dos_stats_analysis
from strudel_string_generators import TEMPERATURE, get_strudel_beats_string_from_dos_dict


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


class MPIDForm(FlaskForm):
    mp_id = StringField("Materials Project ID", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():
    mp_id = None
    form = MPIDForm()

    if form.validate_on_submit():
        mp_id = form.mp_id.data.strip()
        return redirect(url_for("success", mp_id=mp_id))

    return render_template("index.html", form=form, mp_id=mp_id)


@app.route("/success/<mp_id>", methods=["GET", "POST"])
def success(mp_id):
    # replace this with a query from whatever database you're using
    # result = get_result_from_database(mp_id)
    strudel_string = get_strudel_beats_string(mp_id)
    form = MPIDForm()

    if request.method == "GET":
        form.mp_id.data = mp_id

    if form.validate_on_submit():
        new_mp_id = form.mp_id.data.strip()
        return redirect(url_for("success", mp_id=new_mp_id))

    return render_template("success.html", form=form, strudel_string=strudel_string)


def get_strudel_beats_string(mp_id):
    dos_dict = dos_stats_analysis(mp_id=mp_id, temp=TEMPERATURE)
    return get_strudel_beats_string_from_dos_dict(dos_dict, temperature=TEMPERATURE)


if __name__ == "__main__":
    app.run(debug=True)
