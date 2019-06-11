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
    def __init__(self):
        self.conn = sqlite3.connect('events.db', check_same_thread=False)
        self.cur = self.conn.cursor()

        with open("./configs/test.json") as fp:
            self.cfg = json.load(fp)

    def end(self):
        self.conn.commit()
        self.conn.close()

    def new_db(self):
        self.cur.execute(
            '''CREATE TABLE if not exists events (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, run INTEGER, event INTEGER, alert_type TEXT)''')
        self.conn.commit()

    def insert_event(self, run, event, alert_type):
        sql = ''' INSERT INTO events(run, event, alert_type) VALUES(?,?,?) '''
        self.cur.execute(sql, (run, event, alert_type))
        self.conn.commit()

    def process_data(self, data):
        if "text" in data and "channel" in data and "user" in data:
            txt = data["text"]
            user = data["user"]
            channel = data["channel"]
            alert_types = [word for word in self.cfg["listen_to_kw"] if word in txt]

            if len(alert_types) and any(word in channel for word in self.cfg["listen_on_channel"]) and \
                    any(word in user for word in self.cfg["listen_to_user"]):
                print("Found valid alert")
                txt2 = txt.split("Run / Event")[-1]
                runinfo = txt2.splitlines()[1]
                run = runinfo.split("/")[0].strip()
                event = runinfo.split("/")[1].strip()
                alert_type = alert_types[0]  # you can set order in self.cfg but double alerts not expected
                print(alert_type, run, event)
                filename = f"{run}_{event}.txt"
                shutil.copyfile("./example_event.txt", os.path.join("events", filename))
                self.insert_event(run, event, alert_type)
            #     web_client.chat_postMessage(
            #         channel=channel_id,
            #         text=f"Hi <@{user}>!",
            #         thread_ts=thread_ts
            #     )

    def run(self):
        n_retries = 0
        retry_times = [1, 2, 3, 10, 30, 60, 60, 60, 600]
        rtm_client = slack.RTMClient(token=os.environ["SLACKTOKEN"])

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
                print(payload)

        while True:
            try:
                rtm_client.start()
            except ClientConnectorError as clexc:
                sleep_time = retry_times[min(len(retry_times) - 1, n_retries)]
                logging.info(f"Failed connection attempt ({clexc}). Trying to reconnect after {sleep_time}s")
                print(f"Failed connection attempt. Trying to reconnect after {sleep_time}s")
                n_retries += 1
                sleep(sleep_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--createdb", help="initialise table", action="store_true")
    args = parser.parse_args()
    reader = Reader()
    if args.createdb:
        reader.new_db()
    else:
        reader.run()
    reader.end()
    exit(0)
