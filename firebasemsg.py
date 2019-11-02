import argparse
import os

import firebase_admin
from firebase_admin import messaging
from event import Event

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./configs/icecubear-21644-firebase-adminsdk-cxst8-4b9cf06699.json"


def inform_firebase(event: Event, topic: str = "/topics/artest"):
    app = firebase_admin.initialize_app()
    message = messaging.Message(
        notification=messaging.Notification(
            title=f'New {event.alert_type} alert found',
            body=f'{event.time} run/event {event.run}/{event.id}',
        ),

        data={
            'run': str(event.run),
            'event': str(event.id),
            'name': event.alert_type,
            "date": str(event.time),
            "energy": str(event.e_nu),
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
        event1 = Event(run=111111, event_id=12, alert_type="silver", event_time="2019-01-01 11:11:11", e_nu=111.11)
        event2 = Event(run=111111, event_id=13, alert_type="silver", event_time="2019-01-01 11:11:11", e_nu=111.11)
        inform_firebase(event1, topic="/topics/ar")
        inform_firebase(event2, topic="/topics/ar")
