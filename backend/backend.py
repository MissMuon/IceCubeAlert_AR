import argparse
import sqlite3

from flask import Flask, send_from_directory
from flask_restful import Resource, Api

app = Flask(__name__, static_url_path='')

path_to_db = "../events.db"


class Nevents(Resource):
    def get(self):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM events")
        n_events = cur.fetchone()[0]
        print(n_events)
        return {'nevents': n_events}


class LastEvents(Resource):
    def get(self, nevents):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type, e_nu, event_time, nickname, comment,"
                    "ra, dec, angle_err_50, angle_err_90 "
                    "FROM events ORDER BY run DESC, event DESC LIMIT ?", [nevents])
        events = cur.fetchall()
        print(events)
        return {'events': events}

class LastEventsV2(Resource):
    def get(self, nevents):
        conn = sqlite3.connect(path_to_db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type, e_nu, event_time, nickname, comment,"
                    "ra, dec, angle_err_50, angle_err_90,"
                    "mjd, rec_x, rec_y, rec_z, rec_t0, zen_rad, azi_rad, ra_rad, dec_rad "
                    "FROM events ORDER BY run DESC, event DESC LIMIT ?", [nevents])
        events = cur.fetchall()
        events = [dict(ev) for ev in events]
        return {'events': events}


class LastEventsBeforeId(Resource):
    def get(self, nevents, run, event):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type, e_nu, event_time, nickname, comment,"
                    "ra, dec, angle_err_50, angle_err_90 "
                    "FROM events WHERE run < :run OR (run = :run AND event < :event) "
                    "ORDER BY run DESC, event DESC "
                    "LIMIT :nevents",
                    {"run": run, "event": event, "nevents": nevents})
        events = cur.fetchall()
        print(events)
        return {'events': events}

class LastEventsBeforeIdV2(Resource):
    def get(self, nevents, run, event):
        conn = sqlite3.connect(path_to_db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT run, event, alert_type, e_nu, event_time, nickname, comment,"
                    "ra, dec, angle_err_50, angle_err_90,"
                    "mjd, rec_x, rec_y, rec_z, rec_t0, zen_rad, azi_rad, ra_rad, dec_rad "
                    "FROM events WHERE run < :run OR (run = :run AND event < :event) "
                    "ORDER BY run DESC, event DESC "
                    "LIMIT :nevents",
                    {"run": run, "event": event, "nevents": nevents})
        events = cur.fetchall()
        events = [dict(ev) for ev in events]
        return {'events': events}


class Comment(Resource):
    def get(self, run, event):
        conn = sqlite3.connect(path_to_db)
        cur = conn.cursor()
        cur.execute("SELECT comment "
                    "FROM events WHERE run = :run AND event = :event ",
                    {"run": run, "event": event})
        events = cur.fetchone()
        if events:
            events = events[0]
        print(events)
        return {'comment': events}


@app.route('/eventfile/<int:run>/<int:event>')
def send_file(run, event):
    filename = f"{int(run)}_{int(event)}.csv"
    return send_from_directory('../events', filename)


api = Api(app)
api.add_resource(Nevents, '/nevents')
api.add_resource(LastEvents, '/lastevents/<int:nevents>')
api.add_resource(LastEventsV2, '/lasteventsv2/<int:nevents>')
api.add_resource(LastEventsBeforeId, '/lasteventsbeforeid/<int:nevents>/<int:run>/<int:event>')
api.add_resource(LastEventsBeforeIdV2, '/lasteventsbeforeidv2/<int:nevents>/<int:run>/<int:event>')
api.add_resource(Comment, '/comment/<int:run>/<int:event>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="port for server", default=5000)
    parser.add_argument("--host", help="for accept remote set to 0.0.0.0", default="localhost")
    parser.add_argument("--cert", help="e.g. cert.pem", default=None)
    parser.add_argument("--privkey", help="e.g. privkey.pem", default=None)
    args = parser.parse_args()

    kwargs = {"host": args.host, "port": args.port}
    if args.cert and args.privkey:
        kwargs["ssl_context"] = (args.cert, args.privkey)
    print(f"Starting backend with options: {kwargs}")
    app.run(**kwargs)


if __name__ == '__main__':
    main()
