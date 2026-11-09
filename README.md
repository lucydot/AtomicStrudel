# Atomic Strudel

A web application for sonification of atomic vibration data; built with flask, strudel, html and a little css.

- [Materials Project](https://next-gen.materialsproject.org/) = atomic-scale vibrations data
- [Flask](https://flask.palletsprojects.com/en/stable/) = getting and processing data
- [Strudel](https://codeberg.org/uzu/strudel) = producing sound from the data
- html and css = styling in the vein of [html energy](https://html.energy/events.html)


### Running locally

1. Install `flask` and `SingingMaterials`:
```conda install flask pip
pip install "SingingMaterials[mp]"```
2. Set a MP API key in .env file
3. ```flask --app app run --debug```