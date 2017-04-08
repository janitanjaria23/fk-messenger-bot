import os

WELCOME_MESSAGE = "Welcome back. How can I help you locate the address you enter?"
MAPS_IMAGE = "https://jovemnerd.com.br/wp-content/uploads/2016/09/vitrine_googlepkmn-760x428.jpg"
GREETING_TEXT = "Welcome to FB Messenger Bot. Hope we can help you locate the address"

params = {
    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
}
headers = {
    "Content-Type": "application/json"
}

google_maps_url = "http://maps.google.com/maps?q="
