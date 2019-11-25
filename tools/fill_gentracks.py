import argparse
import csv
import json
import os
import subprocess
import sqlite3
import logging

from event import Event

class Reader:
    def __init__(self, cfg: str):
        self.conn = sqlite3.connect('events.db', check_same_thread=False)
        self.cur = self.conn.cursor()

        with open(cfg) as fp:
            self.cfg = json.load(fp)

    def end(self):
        try:
            self.conn.commit()
        except Exception as exc:
            logging.exception(exc)
            logging.error(exc)
            self.conn.rollback()
        self.conn.close()
        logging.shutdown()

    def process_event(self, event: Event):
        # create track data
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./gentrack.sh"), str(event.run), str(event.id)]
        print("cmd", cmd)
        try:
            status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status create track data: {status}")
            filename = f"{event.run}_{event.id}_track.csv"
            cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
                   "./events/"]
            status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status scp gentrack: {status}")
            with open("./events/"+filename) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = list(csv_reader)[0]
                # evtid = row[0]
                mjd = row[1]
                rec_x = row[2]
                rec_y = row[3]
                rec_z = row[4]
                rec_t0 = row[5]
                zen_rad = row[6]
                azi_rad = row[7]
                ra_rad = row[8]
                dec_rad = row[9]
            event.set_track_info(mjd, rec_x, rec_y, rec_z, rec_t0, zen_rad, azi_rad, ra_rad, dec_rad)
            self.update_event_in_db(event)

        except subprocess.CalledProcessError as subprocexc:
            print(subprocexc)

    def update_event_in_db(self, event: Event):
        sql = f''' UPDATE events SET mjd = ?, rec_x = ?, rec_y = ?, rec_z = ?, rec_t0 = ?, zen_rad = ?, azi_rad = ?,
                                     ra_rad = ?, dec_rad = ?
                                 WHERE run = ? and event = ?
               '''
        print(sql)
        try:
            self.cur.execute(sql, [event.mjd, event.rec_x, event.rec_y, event.rec_z, event.rec_t0, event.zen_rad,
                                   event.azi_rad, event.ra_rad, event.dec_rad, event.run, event.id])
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.error(f'(Run, event) already exists: {event.run}, {event.id}')
            self.conn.rollback()
            raise StopIteration
        except Exception as exc:
            logging.exception(exc)
            logging.error(f"DB Insertion error for: {sql}")
            self.conn.rollback()
            raise StopIteration

    def process_all_events(self):
        self.cur.execute("SELECT run, event FROM events ORDER BY run DESC, event DESC")
        data = self.cur.fetchall()
        for datum in data:
            event = Event(run=datum[0], event_id=datum[1])
            self.process_event(event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", help="path to config file", default="./configs/test.json")
    args = parser.parse_args()

    reader = Reader(args.cfg)

    reader.process_all_events()
    reader.end()
    exit(0)
