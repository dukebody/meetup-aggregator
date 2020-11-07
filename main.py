import os

from flask import Flask
from flask import render_template

from utils import load_events, get_database, sort_events

app = Flask(__name__)
database = get_database()


# need to set this variable with `deta update -e .your-env-file`
if bool(os.getenv("RUNNING_IN_DETA")):
    from deta import App as DetaApp
    from sync import sync_meetups

    app = DetaApp(app)

    @app.lib.run(action='sync')
    @app.lib.cron()
    def cron_job(event):
        print("running on a schedule")
        meetup_ids = ["python-barcelona", "python_alc", "PyData-Salamanca"]
        sync_meetups(meetup_ids)
        return "Meetups synced!"


@app.route('/')
def list_events():
    events = load_events(database)
    return render_template(
        'index.html', events=sort_events(events, field="date_time"))
