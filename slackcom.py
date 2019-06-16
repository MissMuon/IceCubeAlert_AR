import argparse
import json
import logging
import os
import sqlite3
import subprocess
from datetime import datetime, timedelta
from time import sleep

import slack
from aiohttp.client_exceptions import ClientConnectorError


class Reader:
    def __init__(self, cfg):
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

    def new_db(self):
        self.cur.execute(
            '''CREATE TABLE if not exists events (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                                                  run INTEGER NOT NULL,
                                                  event INTEGER NOT NULL,
                                                  alert_type TEXT,
                                                  event_time DATETIME,
                                                  e_nu float,
                                                  PRIMARY KEY (run,event)
                                                  )''')
        self.conn.commit()

    def insert_event_into_db(self, run, event, alert_type, e_nu, event_time):
        sql = ''' INSERT INTO events(run, event, alert_type, e_nu, event_time) VALUES(?,?,?,?,?) '''
        try:
            self.cur.execute(sql, (run, event, alert_type, e_nu, event_time))
            self.conn.commit()
        except sqlite3.IntegrityError:
            logging.error(f'(Run, event) already exists: {run}, {event}')
            self.conn.rollback()
        except Exception as exc:
            logging.exception(exc)
            logging.error("DB Insertion error for: ", sql)
            self.conn.rollback()

    def send_fake_event(self):
        """Send example event message to send_to_channel config for testing purposes"""
        for ch in self.cfg["send_to_channel"]:
            print("Sending to", self.cfg["send_to_channel"])
            attachments = [
                {"fallback": "realtimeEvent found. selections: 'neutrino'.  Alerts: gfu-gold",
                 "title": "Alert Information",
                 "id": 1, "color": "a30200",
                 "fields": [{"title": "Event Time (UTC)", "value": "2019-04-22 05:59:42.071572", "short": True},
                            {"title": "Run / Event", "value": "132465 / 3856549", "short": True},
                            {"title": "Signal prob (%) /  FAR (per year)", "value": "51.348% / 1.183", "short": True},
                            {"title": "Muon Energy / Neutrino Energy (TeV)", "value": "133.575 / 169.994",
                             "short": True},
                            {"title": "Event Direction (RA/DEC) (deg)", "value": "167.857 / 17.726", "short": True},
                            {"title": "Angular error 50% (90%)", "value": "0.264 (0.679)", "short": True}],
                 "mrkdwn_in": ["fields"]}]
            text = "realtimeEvent found. selections: 'neutrino'.  Alerts: gfu-gold"
            slack.WebClient(token=os.environ["SLACKTOKEN"]).chat_postMessage(
                channel=ch,
                text=text,
                attachments=attachments
            )

    def inform_channel(self, filepath, alert_type, run, event):
        for ch in self.cfg["send_to_channel"]:
            client = slack.WebClient(token=os.environ['SLACKTOKEN'])
            response = client.files_upload(
                channels=ch,
                file=filepath)
            if not response["ok"]:
                logging.error(f"Could not upload file to channel {ch}:", response)
                continue
            try:
                slack_path = response["file"]["url_private"]
            except KeyError as exc:
                logging.error("Cannot find url to image:", response)
                raise exc

            attachments = [{
                "image_url": slack_path
            }]
            slack.WebClient(token=os.environ["SLACKTOKEN"]).chat_postMessage(
                channel=ch,
                text=f"New preview image for {alert_type} alert. Run / Event: {run} {event}. Check AR app.",
                attachments=attachments
            )

    def process_slack_message_data(self, data):
        # {"type": "message",
        # "subtype": "bot_message",
        #  "text": "...",
        #  "username": "alert-bot",
        #  "icons": {"emoji": ":sparkler:",
        #            "image_64": "https:\/\/a.slack-edge.com\/37d58\/img\/emoji_2017_12_06\/apple\/1f387.png"},
        #  "bot_id": "B04VC4ZJF",
        #  "attachments": [...]

        if "text" in data and "channel" in data and ("username" in data or "user" in data):
            txt = data["text"]
            user = data["username"] if "username" in data else data["user"]
            channel = data["channel"]
            alert_types = [word for word in self.cfg["listen_to_kw"] if word in txt]

            if "realtimeEvent" in txt and len(alert_types) and \
                    any(word in channel for word in self.cfg["listen_on_channel"]) and \
                    any(word in user for word in self.cfg["listen_to_user"]):
                print("Found valid alert")
                fields = data["attachments"][0]["fields"]
                event_time = fields[0]["value"]
                run = fields[1]["value"].split("/")[0].strip()
                event = fields[1]["value"].split("/")[1].strip()
                e_nu = fields[3]["value"].split("/")[1].strip()
                alert_type = alert_types[0]  # you can set order in self.cfg but double alerts not expected
                print("eventtime", event_time)
                self.process_valid_event(alert_type, e_nu, run, event, event_time)

    def process_valid_event(self, alert_type, e_nu, run, event, event_time):
        # get file from south pole
        event_time_dt = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S.%f')
        start = (event_time_dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H:%M:%S")
        stop = (event_time_dt + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./download.sh"), start, stop, run, event]
        print("cmd", cmd)
        status = subprocess.run(cmd, capture_output=True, check=True)
        print("status download", status)
        filename = f"{run}_{event}.csv"
        cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
               "./events/"]
        status = subprocess.run(cmd, capture_output=True, check=True)
        print("status cp", status)

        # insert to db
        print("Inserting event:", alert_type, run, event, event_time, e_nu)
        self.insert_event_into_db(run, event, alert_type, e_nu, event_time)

        # create preview image
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./create_screenshot.sh"), run, event]
        print("cmd", cmd)
        status = subprocess.run(cmd, capture_output=True, check=True)
        print("status create screenshot", status)
        filename = f"{run}_{event}.png"
        cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
               "./events/"]
        status = subprocess.run(cmd, capture_output=True, check=True)
        print("status cp", status)

        # send preview
        try:
            self.inform_channel(os.path.join("./events", filename), alert_type, run, event)
        except Exception as exc:
            logging.error("Could not inform channel", type(exc), exc)

    def run(self):
        n_retries = 0
        retry_times = [1, 2, 3, 10, 30, 60, 60, 60, 600]

        @slack.RTMClient.run_on(event='message')
        def get_run_event(**payload):
            try:
                data = payload['data']
                print(data)
                # web_client = payload['web_client']
                # rtm_client = payload['rtm_client']

                self.process_slack_message_data(data)

            except Exception as e:
                logging.exception(e)
                logging.error(f"Failed payload: {payload}")

        while True:
            try:
                print("Starting event reader")
                rtm_client = slack.RTMClient(token=os.environ["SLACKTOKEN"])
                rtm_client.start()
                print("Event reader run ended")
            except ClientConnectorError as clexc:
                sleep_time = retry_times[min(len(retry_times) - 1, n_retries)]
                logging.info(f"Failed connection attempt ({clexc}). Trying to reconnect after {sleep_time}s")
                print(f"Failed connection attempt. Trying to reconnect after {sleep_time}s")
                n_retries += 1
                sleep(sleep_time)
            except KeyboardInterrupt:
                logging.info("Stopping after keyboard interrupt")
                break
            except Exception as exc:
                logging.exception(exc)
                logging.error("Unhandled exception: restarting reader client after 1 sec")
                sleep(1)

    def remove_event(self, run, event):
        sql = '''DELETE FROM events WHERE run=? AND event=?'''
        try:
            self.cur.execute(sql, (run, event))
            self.conn.commit()
        except Exception as exc:
            logging.exception(exc)
            logging.error("DB deletion error for: ", sql)
            self.conn.rollback()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--createdb", help="initialise table", action="store_true")
    parser.add_argument("--cfg", help="path to config file", default="./configs/test.json")
    parser.add_argument("--sendfake", help="send a fake msg for testing", action="store_true")
    parser.add_argument("--manualInsertEvent", help="alert-type e_nu run event event_time "
                                                    "(e.g. \"gfu-gold\" 32.9 132457 15 \"2019-04-20 01:30:05.162364\")",
                        nargs='+')
    parser.add_argument("--manualDeleteEvent", help="run event (e.g. 132457 15)",
                        nargs='+')
    args = parser.parse_args()
    reader = Reader(args.cfg)
    if args.createdb:
        print("Creating new DB...")
        reader.new_db()
        print("...done")
    elif args.sendfake:
        reader.cfg["send_to_channel"] = reader.cfg["send_to_channel_fake"]
        reader.send_fake_event()
    elif args.manualInsertEvent:
        reader.process_valid_event(args.manualInsertEvent[0],
                                   args.manualInsertEvent[1],
                                   args.manualInsertEvent[2],
                                   args.manualInsertEvent[3],
                                   args.manualInsertEvent[4])
    elif args.manualDeleteEvent:
        reader.remove_event(run=args.manualDeleteEvent[0], event=args.manualDeleteEvent[1])
    else:
        reader.run()
    reader.end()
    exit(0)
