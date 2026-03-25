import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── Your Meta credentials ──────────────────────────────────────────
VERIFY_TOKEN = "my_verify_token_123"   # you can change this string to anything you like
PHONE_NUMBER_ID = "966483603225755"
ACCESS_TOKEN = "EAAVcZCZAhwmTsBRBFOdAXt0WlB4w0G1xIx6VU3e5ZCpLJZAuDfYCfoBbIQs2gts01UI8ZCJofYQhk0idjOGJB7HxLNjy0h9bgWeYFliTGqPjQ710E6hbRoACqGSM3i5Yw7W8xZComoyTdXB5bL3p2jcFXgYOJI9pUJn5p6ZBMoLDCZC7Q4AphWWZBm3VEItTFlqJCjkTPRhLESccC3oa5YNONKWBZAAwEXF3FHGRDBceA98icE23Sg1HJSkoGL0ZBtmsN3z8r5h2jZCen9XaFljZCVpMqgAZDZD"
# ──────────────────────────────────────────────────────────────────

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    try:
        messages = data["entry"][0]["changes"][0]["value"]["messages"]
        for message in messages:
            if message["type"] == "text":
                sender = message["from"]
                text_received = message["text"]["body"]
                print(f"Message from {sender}: {text_received}")

                # ── Your auto-reply message ──────────────────────────
                reply = "Hello! Thanks for reaching out. We will get back to you shortly."
                # ────────────────────────────────────────────────────

                send_whatsapp_message(sender, reply)
    except (KeyError, IndexError):
        pass

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
