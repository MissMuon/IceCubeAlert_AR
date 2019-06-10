import json
import logging
import slack
import os


def main():
    with open("./configs/test.json") as fp:
        cfg = json.load(fp)

    @slack.RTMClient.run_on(event='message')
    def say_hello(**payload):
        try:
            data = payload['data']
            print(data)
            web_client = payload['web_client']
            rtm_client = payload['rtm_client']

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
    rtm_client.start()


if __name__ == "__main__":
    main()
