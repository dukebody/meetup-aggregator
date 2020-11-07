from flask import Flask
from flask import render_template

from main import load_events, FileDatabase

app = Flask(__name__)

database = FileDatabase('events.json')


@app.route('/')
def list_events():
    events = load_events(database, sort_by_dt=True)
    return render_template('events_list.html', events=events)