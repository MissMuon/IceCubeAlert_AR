import argparse
import json
import logging
import os
import shutil
import sqlite3
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

    def insert_event(self, run, event, alert_type, e_nu, event_time):
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

    def process_data(self, data):
        # {
        # 'client_msg_id': '24a6209e-2662-4a9c-9ec9-6f4911d948fd',
        # 'suppress_notification': False,
        # 0 'text': "realtimeEvent found. selections: 'neutrino'.  Alerts: None Prescale applied: 20\n
        # 1 realtimeEvent found. selections: 'neutrino'.  Alerts: gfu-gold\n
        # 2 Alert Information\n
        # 3 Event Time (UTC)\n
        # 4 2019-06-13 19:54:18.125833\n
        # 5 Run / Event\n
        # 6 132684 / 5635104\n
        # 7 Signal prob (%) /  FAR (per year)\n
        # 8 60.793% / 0.719\n
        # 9 Muon Energy / Neutrino Energy (TeV)\n
        # 10 168.409 / 195.353\n
        # 11 Event Direction (RA/DEC) (deg)\n
        # 12 312.407 / 26.504",
        # 'user': 'U03D5NE8C',
        # 'team': 'T02KFGDCN',
        # 'channel': 'DK9CRR9EK',
        # 'event_ts': '1560582790.004400',
        # 'ts': '1560582790.004400'
        # }
        if "text" in data and "channel" in data and ("username" in data or "user" in data):
            txt = data["text"]
            user = data["username"] if "username" in data else data["user"]
            channel = data["channel"]
            alert_types = [word for word in self.cfg["listen_to_kw"] if word in txt]

            if len(alert_types) and any(word in channel for word in self.cfg["listen_on_channel"]) and \
                    any(word in user for word in self.cfg["listen_to_user"]):
                print("Found valid alert")
                txt = txt.splitlines()
                event_time = txt[4].strip()
                run = txt[6].split("/")[0].strip()
                event = txt[6].split("/")[1].strip()
                e_nu = txt[10].split("/")[1].strip()
                alert_type = alert_types[0]  # you can set order in self.cfg but double alerts not expected
                print("Inserting:", alert_type, run, event, event_time, e_nu)
                filename = f"{run}_{event}.txt"
                shutil.copyfile("./example_event.txt", os.path.join("events", filename))
                self.insert_event(run, event, alert_type, e_nu, event_time)
            #     web_client.chat_postMessage(
            #         channel=channel_id,
            #         text=f"Hi <@{user}>!",
            #         thread_ts=thread_ts
            #     )

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

                self.process_data(data)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--createdb", help="initialise table", action="store_true")
    parser.add_argument("--cfg", help="path to config file", default="./configs/test.json")
    args = parser.parse_args()
    reader = Reader(args.cfg)
    if args.createdb:
        print("Creating new DB...")
        reader.new_db()
        print("...done")
    else:
        reader.run()
    reader.end()
    exit(0)
