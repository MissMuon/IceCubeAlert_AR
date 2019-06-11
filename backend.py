import argparse
import sqlite3

from flask import Flask, send_from_directory
from flask_restful import Resource, Api

app = Flask(__name__, static_url_path='')


class Nevents(Resource):
    def get(self):
        conn = sqlite3.connect("events.db")
        cur = conn.cursor()
        cur.execute("select count(*) from events")
        n_events = cur.fetchone()[0]
        print(n_events)
        return {'nevents': n_events}


class LastEvents(Resource):
    def get(self, nevents):
        conn = sqlite3.connect("events.db")
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type from events ORDER BY run DESC, event DESC LIMIT ?", [nevents])
        events = cur.fetchall()
        print(events)
        return {'events': events}


@app.route('/eventfile/<int:run>/<int:event>')
def send_file(run, event):
    filename = f"{int(run)}_{int(event)}.txt"
    return send_from_directory('events', filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port for server", default=5000)
    args = parser.parse_args()

    api = Api(app)
    api.add_resource(Nevents, '/nevents')
    api.add_resource(LastEvents, '/lastevents/<nevents>')
    app.run(port=args.port)


if __name__ == '__main__':
    main()
