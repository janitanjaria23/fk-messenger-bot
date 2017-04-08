import os
import sys
import json

import requests
from flask import Flask, request
import config as cfg
import google_api_key

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

                    send_message(sender_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def get_google_geocoding_api_response(address):
    google_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = google_api_key.api_key
    location = None
    try:
        r = requests.get(google_url, params=dict(address=address, key=api_key))
        resp = r.json()
        log(resp)
        if 'results' in resp and len(resp['results']) > 0:
            location = ','.join([str(resp['results'][0]['geometry']['location']['lat']), str(resp['results'][0]['geometry']['location']['lng'])])
    except Exception as err:
        log(err)

    return location


def send_first_message(recipient_id, message_text):
    first_msg_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        # "setting_type": "greeting",
        "message": {
            "text": message_text
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


def send_attachment_message(recipient_id, attachment_message):
    attachment_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": attachment_message
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


def send_message(recipient_id, message_text):
    log("sending message to {recipient}".format(recipient=recipient_id))

    send_greeting_message(recipient_id)
    send_first_message(recipient_id, cfg.WELCOME_MESSAGE)
    attachment_message = cfg.TENNIS_CHAMP_IMAGE
    send_attachment_message(recipient_id, attachment_message)
    location = get_google_geocoding_api_response(message_text)
    log("Google Location: " + str(location))
    location_message = "The latitude and longitude of the given address is : " + str(location)
    # attachment_message = cfg.google_maps_url + str(location)
    attachment_message = "https://maps.googleapis.com/maps/api/staticmap?key=" + str(google_api_key.api_key) + "&markers=color:red|label:B|" + str(location) + "&size=360x360&zoom=13"
    log("Google Maps URL: " + str(attachment_message))
    send_first_message(recipient_id, location_message)
    send_attachment_message(recipient_id, attachment_message)


def log(message):
    print str(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug=True)
