import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

VERIFY_TOKEN = "my_verify_token_123"
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
YOUR_NUMBER = "2348086137316"
DASHBOARD_PASSWORD = "#Clint4real"

conversation_state = {}
message_log = []

RULE1_TRIGGER = "from stream website, i'm ready to get started on stream. how do i continue and what are the requirements?"

REPLY_1 = (
    "💚 Welcome to Stream Africa 💚\n\n"
    "We're excited to have you here!\n\n"
    "To get started with your registration, please tell us your full name.\n\n"
    "What's your name? 😊"
)

REPLY_2 = (
    "💚 HOW STREAM AFRICA WORKS 💚\n\n"
    "Stream Africa is a digital earning platform where you make money from livestreams, videos, audio, snaps, and downloads.\n\n"
    "🏆 MEMBERSHIP DETAILS\n"
    "• Onboarding Fee – ₦12,000\n"
    "• Instant Cashback – ₦12,000 (100% returned immediately)\n"
    "• Partner Earnings – ₦10,200\n"
    "• Reconnect – ₦300\n"
    "• Partner Chain 1 – ₦200\n"
    "• Partner Chain 2 – ₦100\n\n"
    "✅ Your ₦12,000 comes back instantly.\n"
    "After that, you begin earning from platform activities.\n\n"
    "💸 DAILY EARNINGS\n"
    "• Livestream Collab – ₦5,700\n"
    "• Video Collab – ₦2,750\n"
    "• Audio Collab – ₦1,550\n"
    "• Snap Collab – ₦1,150\n"
    "• File Download – ₦1,050\n\n"
    "🔥 The more active you are, the more you earn.\n\n"
    "🏦 WITHDRAWALS\n"
    "Withdraw directly to your local bank account.\n"
    "Payout details are shown inside your dashboard.\n\n"
    "✨ Fast recovery. Daily income. Multiple earning streams.\n\n"
    "Ready to join?\n"
    "Comment: \"I want to join Stream Africa\""
)

REPLY_3 = (
    "🚀 READY TO GET STARTED WITH STREAM?\n\n"
    "To begin your registration, complete your payment using the details below:\n\n"
    "Amount: ₦12,000\n\n"
    "Account Name: Raenest / Clinton Uchenna Spino\n"
    "Bank Name: Kredi Money MFB Ltd\n"
    "Account Number: 1807561116\n\n"
    "After making payment, send your payment receipt immediately for confirmation and activation.\n\n"
    "⚡ Faster confirmation = Faster activation.\n"
    "Secure your spot now and get started without delay."
)

SIMILAR_KEYWORDS = ["i want to join", "join", "join stream", "i want to join stream africa"]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stream Africa Bot Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 20px; }
        h1 { color: #25D366; margin-bottom: 5px; }
        .subtitle { color: #888; font-size: 13px; margin-bottom: 25px; }
        .stats { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 25px; }
        .stat-box { background: #1a1a1a; border-radius: 10px; padding: 15px 25px; min-width: 140px; }
        .stat-box .number { font-size: 28px; font-weight: bold; }
        .stat-box .label { font-size: 12px; color: #888; margin-top: 4px; }
        .green { color: #25D366; }
        .red { color: #e74c3c; }
        .yellow { color: #f1c40f; }
        .blue { color: #3498db; }
        table { width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 10px; overflow: hidden; }
        th { background: #222; padding: 12px 15px; text-align: left; font-size: 12px; color: #888; text-transform: uppercase; }
        td { padding: 12px 15px; border-top: 1px solid #2a2a2a; font-size: 13px; vertical-align: top; }
        tr:hover { background: #222; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .badge-success { background: #1a3a2a; color: #25D366; }
        .badge-failed { background: #3a1a1a; color: #e74c3c; }
        .badge-ignored { background: #2a2a1a; color: #f1c40f; }
        .badge-inbound { background: #1a2a3a; color: #3498db; }
        .msg { max-width: 300px; white-space: pre-wrap; word-break: break-word; }
        .login-box { max-width: 360px; margin: 100px auto; background: #1a1a1a; padding: 40px; border-radius: 12px; }
        .login-box h2 { color: #25D366; margin-bottom: 20px; text-align: center; }
        input[type=password] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #111; color: #fff; font-size: 15px; margin-bottom: 15px; }
        button { width: 100%; padding: 12px; background: #25D366; color: #000; border: none; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; }
        button:hover { background: #1ebe5a; }
        .error { color: #e74c3c; text-align: center; margin-bottom: 15px; font-size: 13px; }
        .refresh { float: right; font-size: 12px; color: #888; margin-bottom: 10px; }
    </style>
</head>
<body>
{% if not authenticated %}
<div class="login-box">
    <h2>🔒 Bot Monitor</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
        <input type="password" name="password" placeholder="Enter password" autofocus>
        <button type="submit">Login</button>
    </form>
</div>
{% else %}
<h1>📊 Stream Africa Bot Monitor</h1>
<p class="subtitle">Live activity log — refresh the page to see latest messages</p>

<div class="stats">
    <div class="stat-box"><div class="number green">{{ stats.total_inbound }}</div><div class="label">Messages Received</div></div>
    <div class="stat-box"><div class="number green">{{ stats.total_success }}</div><div class="label">Replies Sent</div></div>
    <div class="stat-box"><div class="number red">{{ stats.total_failed }}</div><div class="label">Failed Replies</div></div>
    <div class="stat-box"><div class="number yellow">{{ stats.total_ignored }}</div><div class="label">Ignored Messages</div></div>
    <div class="stat-box"><div class="number blue">{{ stats.unique_senders }}</div><div class="label">Unique Contacts</div></div>
</div>

<p class="refresh">Showing last {{ logs|length }} events</p>
<table>
    <thead>
        <tr>
            <th>Time</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Message</th>
            <th>Step</th>
        </tr>
    </thead>
    <tbody>
    {% for entry in logs|reverse %}
        <tr>
            <td>{{ entry.time }}</td>
            <td>{{ entry.phone }}</td>
            <td><span class="badge badge-{{ entry.status_class }}">{{ entry.status }}</span></td>
            <td><div class="msg">{{ entry.message }}</div></td>
            <td>{{ entry.step }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
{% endif %}
</body>
</html>
"""


def log_event(phone, status, status_class, message, step):
    message_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone,
        "status": status,
        "status_class": status_class,
        "message": message[:200],
        "step": step
    })
    if len(message_log) > 500:
        message_log.pop(0)


def is_similar_to_join(text):
    text = text.lower().strip()
    return any(keyword in text for keyword in SIMILAR_KEYWORDS)


def send_whatsapp_message(to, message, step):
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
    result = response.json()

    if "error" in result:
        error_msg = result["error"].get("message", "Unknown error")
        error_code = result["error"].get("code", "Unknown code")
        print(f"[FAILED] Message to {to} failed. Code: {error_code}. Reason: {error_msg}")
        log_event(to, "FAILED", "failed", f"Error {error_code}: {error_msg}", step)
        notify_owner(to, error_msg, error_code)
    else:
        print(f"[SUCCESS] Message sent to {to}")
        log_event(to, "SENT", "success", message[:100], step)

    return result


def notify_owner(failed_to, error_msg, error_code):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    notification = (
        f"⚠️ Message Failure Alert\n"
        f"Failed to reply to: {failed_to}\n"
        f"Error code: {error_code}\n"
        f"Reason: {error_msg}"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": YOUR_NUMBER,
        "type": "text",
        "text": {"body": notification}
    }
    requests.post(url, headers=headers, json=payload)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    authenticated = False
    error = None

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == DASHBOARD_PASSWORD:
            authenticated = True
        else:
            error = "Wrong password. Try again."

    if authenticated:
        stats = {
            "total_inbound": sum(1 for e in message_log if e["status"] == "INBOUND"),
            "total_success": sum(1 for e in message_log if e["status"] == "SENT"),
            "total_failed": sum(1 for e in message_log if e["status"] == "FAILED"),
            "total_ignored": sum(1 for e in message_log if e["status"] == "IGNORED"),
            "unique_senders": len(set(e["phone"] for e in message_log if e["status"] == "INBOUND"))
        }
        return render_template_string(DASHBOARD_HTML, authenticated=True, logs=message_log, stats=stats)

    return render_template_string(DASHBOARD_HTML, authenticated=False, error=error, logs=[], stats={})


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
                text = message["text"]["body"].strip()
                print(f"[INBOUND] From {sender}: {text}")

                step = conversation_state.get(sender, 0)
                log_event(sender, "INBOUND", "inbound", text, step)

                if step == 0 and text.lower() == RULE1_TRIGGER.lower():
                    send_whatsapp_message(sender, REPLY_1, 1)
                    conversation_state[sender] = 1

                elif step == 1:
                    send_whatsapp_message(sender, REPLY_2, 2)
                    conversation_state[sender] = 2

                elif step == 2 and is_similar_to_join(text):
                    send_whatsapp_message(sender, REPLY_3, 3)
                    conversation_state[sender] = 3

                else:
                    print(f"[IGNORED] No rule matched for {sender} at step {step}: {text}")
                    log_event(sender, "IGNORED", "ignored", text, step)

    except (KeyError, IndexError):
        pass

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
