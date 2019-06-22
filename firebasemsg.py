import argparse
import os

import firebase_admin
from firebase_admin import messaging

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./configs/icecubear-21644-firebase-adminsdk-cxst8-4b9cf06699.json"


def inform_firebase(run: int, event: int, alert_type: str, time, energy: float, topic: str = "/topics/artest"):
    app = firebase_admin.initialize_app()
    message = messaging.Message(
        notification=messaging.Notification(
            title=f'New {alert_type} alert found',
            body=f'{time} run/event {run}/{event}',
        ),

        data={
            'run': str(run),
            'event': str(event),
            'name': alert_type,
            "date": str(time),
            "energy": str(energy),
        },
        topic=topic,
    )

    response = messaging.send(message)
    print('Successfully sent to firebase:', response)
    firebase_admin.delete_app(app)


def send_notification(title, note, topic):
    app = firebase_admin.initialize_app()
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=note,
        ),
        topic=topic,
    )

    response = messaging.send(message)
    print('Successfully sent to firebase:', response)
    firebase_admin.delete_app(app)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--notification", help="send a notification to users", action="store_true")
    parser.add_argument("--title", help="title to send if --notification")
    parser.add_argument("--note", help="text to send if --notification")
    parser.add_argument("--topic", help="topic to send to if --notification", default="/topics/artest")
    args = parser.parse_args()

    if args.notification:
        send_notification(args.title, args.note, args.topic)
    else:
        inform_firebase(111111, 12, "silver", "2019-01-01 11:11:11", 111.11, topic="/topics/ar")
        inform_firebase(111111, 13, "silver", "2019-01-01 11:11:11", 111.11, topic="/topics/ar")
