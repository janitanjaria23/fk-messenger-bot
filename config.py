import os

WELCOME_MESSAGE = "Padharo Mare Desh"
TENNIS_CHAMP_IMAGE = "https://www.oneyoungworld.com/sites/oneyoungworld.com/files/images/roger-federer.jpg"
GREETING_TEXT = "Welcome to Janit's Test Bot... Happy to hear from you"

params = {
    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
}
headers = {
    "Content-Type": "application/json"
}

google_maps_url = "http://maps.google.com/maps?q="
