import argparse
import logging
import sqlite3

from flask import Flask, send_from_directory
from flask_restful import Resource, Api

app = Flask(__name__, static_url_path='')


class Nevents(Resource):
    def get(self):
        conn = sqlite3.connect("events.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM events")
        n_events = cur.fetchone()[0]
        print(n_events)
        return {'nevents': n_events}


class LastEvents(Resource):
    def get(self, nevents):
        conn = sqlite3.connect("events.db")
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type FROM events ORDER BY run DESC, event DESC LIMIT ?", [nevents])
        events = cur.fetchall()
        print(events)
        return {'events': events}


class LastEventsBeforeId(Resource):
    def get(self, nevents, run, event):
        conn = sqlite3.connect("events.db")
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type FROM events WHERE run < :run OR (run = :run AND event < :event) "
                    "ORDER BY run DESC, event DESC "
                    "LIMIT :nevents",
                    {"run": run, "event": event, "nevents": nevents})
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
    parser.add_argument("--host", help="for accept remote set to 0.0.0.0", default="localhost")
    parser.add_argument("--cert", help="e.g. cert.pem", default=None)
    parser.add_argument("--privkey", help="e.g. privkey.pem", default=None)
    args = parser.parse_args()

    api = Api(app)
    api.add_resource(Nevents, '/nevents')
    api.add_resource(LastEvents, '/lastevents/<int:nevents>')
    api.add_resource(LastEventsBeforeId, '/lasteventsbeforeid/<int:nevents>/<int:run>/<int:event>')
    kwargs = {"host": args.host, "port": args.port}
    if args.cert and args.privkey:
        kwargs["ssl_context"] = (args.cert, args.privkey)
    print(f"Starting backend with options: {kwargs}")
    while True:
        try:
            app.run(**kwargs)
        except Exception as exc:
            logging.exception(exc)


if __name__ == '__main__':
    main()
