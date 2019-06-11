import json
import logging
import os
from time import sleep

import slack
from aiohttp.client_exceptions import ClientConnectorError


def main():
    n_retries = 0
    retry_times = [1, 2, 3, 10, 30, 60, 60, 60, 600]
    with open("./configs/test.json") as fp:
        cfg = json.load(fp)

    @slack.RTMClient.run_on(event='message')
    def get_run_event(**payload):
        try:
            data = payload['data']
            print(data)
            # web_client = payload['web_client']
            # rtm_client = payload['rtm_client']

            if "text" in data and "channel" in data and "user" in data:
                txt = data["text"]
                user = data["user"]
                channel = data["channel"]
                if any(word in channel for word in cfg["listen_on_channel"]) and \
                        any(word in txt for word in cfg["listen_to_kw"]) and \
                        any(word in user for word in cfg["listen_to_user"]):
                    print("Found valid alert")
                    txt2 = txt.split("Run / Event")[-1]
                    runinfo = txt2.splitlines()[1]
                    run = runinfo.split("/")[0].strip()
                    info = runinfo.split("/")[1].strip()
                    print(run, info)

                #     web_client.chat_postMessage(
                #         channel=channel_id,
                #         text=f"Hi <@{user}>!",
                #         thread_ts=thread_ts
                #     )

        except Exception as e:
            logging.exception(e)
            print(payload)

    rtm_client = slack.RTMClient(token=os.environ["SLACKTOKEN"])
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
    main()
