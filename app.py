import os
import sys
import json

import requests
from flask import Flask, request
import config as cfg

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"][
                        "id"]
                    message_text = messaging_event["message"]["text"] # this is the text of the message

                    send_message(sender_id)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_first_message(recipient_id):
    first_msg_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        # "setting_type": "greeting",
        "message": {
            "text": cfg.WELCOME_MESSAGE
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=cfg.params, headers=cfg.headers,
                      data=first_msg_data)
    if r.status_code != 200:
        log(r.status_code)
        log("Response text: ")
        log(r.text)


def send_greeting_message(recipient_id):
    greeting_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "setting_type": "greeting",
        "greeting": {
            "text": cfg.GREETING_TEXT
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/thread_settings", params=cfg.params, headers=cfg.headers,
                      data=greeting_data)
    if r.status_code != 200:
        log(r.status_code)
        log("Response text: ")
        log(r.text)
    log("greeting message sent")


def send_attachment_message(recipient_id):
    attachment_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": cfg.TENNIS_CHAMP_IMAGE
                }
            }
        }
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=cfg.params, headers=cfg.headers,
                      data=attachment_data)
    if r.status_code != 200:
        log(r.status_code)
        log("Response text: ")
        log(r.text)


def send_message(recipient_id):
    log("sending message to {recipient}".format(recipient=recipient_id))

    send_greeting_message(recipient_id)
    send_first_message(recipient_id)
    send_attachment_message(recipient_id)


def log(message):
    print str(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug=True)
