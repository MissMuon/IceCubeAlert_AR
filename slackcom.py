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

from event import Event
from firebasemsg import inform_firebase


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

    def new_db(self):
        self.cur.execute(
            '''CREATE TABLE if not exists events (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                                                  run INTEGER NOT NULL,
                                                  event INTEGER NOT NULL,
                                                  alert_type TEXT,
                                                  event_time DATETIME,
                                                  signal_prob FLOAT,
                                                  far FLOAT,
                                                  e_nu FLOAT,
                                                  e_mu FLOAT,
                                                  ra FLOAT,
                                                  dec FLOAT,
                                                  angle_err_50 FLOAT,
                                                  angle_err_90 FLOAT,
                                                  nickname TEXT,
                                                  comment TEXT,
                                                  PRIMARY KEY (run,event)
                                                  )''')
        self.conn.commit()

    def insert_event_into_db(self, event: Event):
        sql = f''' INSERT INTO events({event.propsstr()}) VALUES({("?," * len(event.propnames))[:-1]}) '''
        try:
            self.cur.execute(sql, event.props)
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

    def inform_channel(self, filepath: str, event: Event, has_screenshot: bool):
        for ch in self.cfg["send_to_channel"]:
            client = slack.WebClient(token=os.environ['SLACKTOKEN'])
            attachments = []
            if has_screenshot:
                response = client.files_upload(
                    channels=ch,
                    file=filepath)
                if response["ok"]:
                    try:
                        slack_path = response["file"]["url_private"]
                    except KeyError as exc:
                        logging.error(f"Cannot find url to image: {response}")
                        raise exc

                    attachments = [{
                        "image_url": slack_path
                    }]
                else:
                    logging.error(f"Could not upload file to channel {ch}: {response}")
            client.chat_postMessage(
                channel=ch,
                text=f"New preview image for {event.alert_type} alert. Run / Event: {event.run} {event.id}. "
                f"Check AR app.",
                as_user=True,
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
            event = Event()

            if "realtimeEvent" in txt and len(alert_types) and \
                    any(word in channel for word in self.cfg["listen_on_channel"]) and \
                    any(word in user for word in self.cfg["listen_to_user"]):
                logging.info("Found valid alert")
                fields = data["attachments"][0]["fields"]
                event.time = fields[0]["value"]
                event.run = fields[1]["value"].split("/")[0].strip()
                event.id = fields[1]["value"].split("/")[1].strip()
                event.signal_prob = fields[2]["value"].split("/")[0].strip()
                event.far = fields[2]["value"].split("/")[1].strip()
                event.e_mu = fields[3]["value"].split("/")[0].strip()
                event.e_nu = fields[3]["value"].split("/")[1].strip()
                event.ra = fields[4]["value"].split("/")[0].strip()
                event.dec = fields[4]["value"].split("/")[1].strip()
                event.angle_err_50 = fields[5]["value"].split("/")[0].strip()
                event.angle_err_90 = fields[5]["value"].split("/")[1].strip()
                event.alert_type = alert_types[0]  # you can set order in self.cfg but double alerts not expected
                print("eventtime", event.time)
                self.process_valid_event(event)

    def process_valid_event(self, event: Event):
        # get file from south pole
        event_time_dt = datetime.strptime(event.time, '%Y-%m-%d %H:%M:%S.%f')
        start = (event_time_dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H:%M:%S")
        stop = (event_time_dt + timedelta(seconds=1)).strftime("%Y-%m-%d %H:%M:%S")
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./download.sh"), start, stop, event.run, event.id]
        print("cmd", cmd)
        wait_times = [15, 15, 30, 60, 60, 120]
        for wait_time in wait_times:
            try:
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
            status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status cp csv: {status}")
        except Exception as e:
            logging.exception(e)
            logging.error(f"scp failed: {e}")

        # insert to db
        logging.info(f"Inserting event: {str(event)}")
        try:
            self.insert_event_into_db(event)
        except StopIteration:
            logging.warning("Stopping further processing of valid event")
            return

        # create preview image
        cmd = ["ssh", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"],
               os.path.join(self.cfg["thinlink_path"], "./create_screenshot.sh"), event.run, event.id]
        print("cmd", cmd)
        has_screenshot = True
        try:
            status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status create screenshot: {status}")
            filename = f"{event.run}_{event.id}.png"
            cmd = ["scp", self.cfg["thinlink_user"] + "@" + self.cfg["thinlink_host"] + f":/tmp/{filename}",
                   "./events/"]
            status = subprocess.run(cmd, capture_output=True, check=True)
            logging.debug(f"status scp screenshot: {status}")
        except subprocess.CalledProcessError as subprocexc:
            logging.exception(subprocexc)
            has_screenshot = False

        # send preview
        try:
            self.inform_channel(os.path.join("./events", filename), event, has_screenshot)
        except Exception as exc:
            logging.error(f"Could not inform channel {type(exc)} {exc}")

        # send firebase
        try:
            inform_firebase(event, topic=self.cfg["firebase_topic"])
        except Exception as exc:
            logging.error(f"Could not inform firebase {type(exc)} {exc}")

    def run(self):
        n_retries = 0
        retry_times = [1, 2, 3, 10, 30, 60, 60, 60, 600]

        @slack.RTMClient.run_on(event='message')
        def get_run_event(**payload):
            logging.info("Enter per message")
            try:
                data = payload['data']
                print(data)
                # web_client = payload['web_client']
                # rtm_client = payload['rtm_client']

                self.process_slack_message_data(data)

            except Exception as rtmexc:
                logging.exception(rtmexc)
                logging.error(f"Failed payload: {payload}")
                raise rtmexc
            logging.info("Exit per message")

        while True:
            try:
                print("Starting event reader")
                rtm_client = slack.RTMClient(token=os.environ["SLACKTOKEN"])
                rtm_client.start()
                print("Event reader run ended")
            except ClientConnectorError as clexc:
                sleep_time = retry_times[min(len(retry_times) - 1, n_retries)]
                logging.warning(f"Failed connection attempt ({clexc}). Trying to reconnect after {sleep_time}s")
                print(f"Failed connection attempt. Trying to reconnect after {sleep_time}s")
                n_retries += 1
                sleep(sleep_time)
            except KeyboardInterrupt as e:
                logging.warning("Stopping after keyboard interrupt")
                raise e
                # break
            except Exception as exc:
                logging.exception(exc)
                logging.error("Unhandled exception: restarting reader client after 1 sec")
                sleep(1)

    def remove_event(self, run: int, event_id: int):
        sql = '''DELETE FROM events WHERE run=? AND event=?'''
        try:
            self.cur.execute(sql, (run, event_id))
            self.conn.commit()
        except Exception as exc:
            logging.exception(exc)
            logging.error(f"DB deletion error for: {sql}")
            self.conn.rollback()

    def add_commnt(self, run: int, event_id: int, comment: str):
        sql = '''UPDATE events SET comment=? WHERE run=? AND event=?'''
        try:
            self.cur.execute(sql, (comment, run, event_id))
            self.conn.commit()
        except Exception as exc:
            logging.exception(exc)
            logging.error(f"DB comment update error for: {sql}")
            self.conn.rollback()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename='./slackcom.log', filemode='w',
                        format='%(asctime)s %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    parser = argparse.ArgumentParser()
    parser.add_argument("--createdb", help="initialise table", action="store_true")
    parser.add_argument("--cfg", help="path to config file", default="./configs/test.json")
    parser.add_argument("--sendfake", help="send a fake msg for testing", action="store_true")
    parser.add_argument("--manualInsertEvent", help=f"{Event.propsstr()} "
    "(e.g. \"gfu-gold\" 51.348 1.183 133.575 169.994 167.857 17.726 "
    "0.264 0.679 132465 3856549 \"2019-04-22 05:59:42.071572\")",
                        nargs='+')
    parser.add_argument("--manualDeleteEvent", help="run event (e.g. 132457 15)",
                        nargs='+')
    parser.add_argument("--manualAddComment", help="run event comment (e.g. 132457 15 \"foo\")",
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
        event1 = Event(args.manualInsertEvent[0],
                       args.manualInsertEvent[1],
                       args.manualInsertEvent[2],
                       args.manualInsertEvent[3],
                       args.manualInsertEvent[4],
                       args.manualInsertEvent[5],
                       args.manualInsertEvent[6],
                       args.manualInsertEvent[7],
                       args.manualInsertEvent[8],
                       args.manualInsertEvent[9],
                       args.manualInsertEvent[10],
                       args.manualInsertEvent[11])
        reader.process_valid_event(event1)
    elif args.manualDeleteEvent:
        reader.remove_event(run=args.manualDeleteEvent[0], event_id=args.manualDeleteEvent[1])
    elif args.manualAddComment:
        reader.add_commnt(run=args.manualAddComment[0], event_id=args.manualAddComment[1],
                          comment=args.manualAddComment[2])
    else:
        reader.run()
    reader.end()
    exit(0)
