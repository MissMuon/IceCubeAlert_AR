import argparse
import csv
import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from time import sleep

sys.path.append(".")

from event import Event


class Reader:
    def __init__(self, cfg: str, haveFiles: bool):
        self.conn = sqlite3.connect('events.db', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.haveFiles = haveFiles

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
        # get file
        event_time_dt = datetime.strptime(event.time, '%Y-%m-%d %H:%M:%S.%f')
        start = (event_time_dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H:%M:%S")
        stop = (event_time_dt + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./download.sh"), start, stop, str(event.run), str(event.id)]
        print("cmd", cmd)
        wait_times = [15, 15, 30, 60, 60, 120]
        for wait_time in wait_times:
            try:
                status = 0
                if not self.haveFiles:
                    status = subprocess.run(cmd, capture_output=True, check=True)
            except subprocess.CalledProcessError:
                if wait_time == wait_times[-1]:
                    logging.error("Could not thinlink event after retrying")
                    return
                logging.info(f"Event file not available yet, sleeping {wait_time}s")
                sleep(wait_time)
                continue
            logging.debug(f"status download: {status}")
            break
        filename = f"{event.run}_{event.id}.csv"
        cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
               "./events/"]
        try:
            status = 0
            if not self.haveFiles:
                status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status cp csv: {status}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"scp failed: {e}")

        # create track data
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./gentrack.sh"), str(event.run), str(event.id)]
        print("cmd", cmd)
        try:
            status = 0
            if not self.haveFiles:
                status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status create track data: {status}")
            filename = f"{event.run}_{event.id}_track.csv"
            cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
                   "./events/"]
            status = 0
            if not self.haveFiles:
                status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status scp gentrack: {status}")
            with open("./events/" + filename) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = list(csv_reader)[0]
                # order: 0 run_id, 1 azi_rad, 2 dec_rad, 3 evtid, 4 mjd, 5 ra_rad, 6 rec_t0, 7 rec_x, 8 rec_y, 9 rec_z, 10 zen_rad
                azi_rad = row[1]
                dec_rad = row[2]
                mjd = row[4]
                ra_rad = row[5]
                rec_t0 = row[6]
                rec_x = row[7]
                rec_y = row[8]
                rec_z = row[9]
                zen_rad = row[10]
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
            print(f"Updated event {event.run}/{event.id}")

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
        self.cur.execute("SELECT run, event, event_time FROM events ORDER BY run DESC, event DESC")
        data = self.cur.fetchall()
        for datum in data:
            event = Event(run=datum[0], event_id=datum[1], event_time=datum[2])
            self.process_event(event)

    def process_one_event(self, run, event):
        self.cur.execute("SELECT run, event, event_time FROM events WHERE run=? AND event=? ORDER BY run DESC, event DESC", (str(run), str(event)))
        data = self.cur.fetchall()
        for datum in data:
            event = Event(run=datum[0], event_id=datum[1], event_time=datum[2])
            self.process_event(event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", help="path to config file for thinlink (grappa) information", default="./configs/test.json")
    parser.add_argument("--haveFiles", help="have files locally? don't download", action="store_true")
    parser.add_argument("--run", help="specific run otherwise all events", default=None)
    parser.add_argument("--event", help="specific event otherwise all events", default=None)
    args = parser.parse_args()

    if (args.run and not args.event) or (args.event and not args.run):
        print("Needs both event and run")
        exit(1)

    reader = Reader(args.cfg, args.haveFiles)

    if args.run:
        reader.process_one_event(args.run, args.event)
    else:
        reader.process_all_events()
    reader.end()
    exit(0)
