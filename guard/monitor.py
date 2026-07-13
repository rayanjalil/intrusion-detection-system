import time
import os
import smtplib
import requests
from email.mime.text import MIMEText
from collections import defaultdict
from datetime import datetime

LOG_FILE = "/data/attempts.log"
BLOCKED_FILE = "/data/blocked_ips.txt"
INCIDENTS_FILE = "/data/incidents.log"
FAIL_THRESHOLD = 5
TIME_WINDOW_SECONDS = 30

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")
ALERT_RECIPIENT = os.environ.get("ALERT_RECIPIENT")
HF_TOKEN = os.environ.get("HF_TOKEN")

failed_attempts = defaultdict(list)
already_alerted = set()

def send_alert_email(ip, num_attempts):
    subject = f"🚨 Security Alert: Brute-force attack detected from {ip}"
    body = (
        f"Intrusion Detection System Alert\n\n"
        f"Suspicious activity detected and blocked.\n\n"
        f"IP Address: {ip}\n"
        f"Failed Attempts: {num_attempts} in {TIME_WINDOW_SECONDS} seconds\n"
        f"Action Taken: IP has been blocked\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ALERT_RECIPIENT

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, [ALERT_RECIPIENT], msg.as_string())
        print(f"📧 Alert email sent to {ALERT_RECIPIENT}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def block_ip(ip):
    with open(BLOCKED_FILE, "a") as f:
        f.write(ip + "\n")
    print(f"🚫 BLOCKED IP: {ip}")

def generate_ai_summary(ip, num_attempts):
    prompt = (
        f"Write a single, concise sentence for a security incident report. "
        f"IP address {ip} made {num_attempts} failed login attempts within "
        f"{TIME_WINDOW_SECONDS} seconds and has been automatically blocked. "
        f"Describe this as a likely brute-force attack and recommend next steps."
    )

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 80}},
            timeout=15
        )
        result = response.json()
        summary = result[0]["generated_text"].replace(prompt, "").strip()
    except Exception as e:
        summary = f"[AI summary unavailable: {e}] {num_attempts} failed attempts from {ip} — likely brute-force attack, IP blocked."

    with open(INCIDENTS_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {ip} | {summary}\n")

    print(f"🧠 AI Summary: {summary}")
    return summary

def check_line(line):
    line = line.strip()
    if not line:
        return
    parts = line.split(",")
    if len(parts) != 4:
        return

    timestamp_str, ip, username, result = parts
    if result != "FAIL":
        return

    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    failed_attempts[ip].append(timestamp)

    cutoff = timestamp.timestamp() - TIME_WINDOW_SECONDS
    failed_attempts[ip] = [t for t in failed_attempts[ip] if t.timestamp() >= cutoff]

    if len(failed_attempts[ip]) >= FAIL_THRESHOLD and ip not in already_alerted:
        num = len(failed_attempts[ip])
        print(f"⚠️  ALERT: Brute-force detected from {ip} — {num} failed attempts in {TIME_WINDOW_SECONDS}s")
        already_alerted.add(ip)
        block_ip(ip)
        send_alert_email(ip, num)
        generate_ai_summary(ip, num)

def follow(file):
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(1)
            continue
        yield line

print("Guard is watching attempts.log...")

with open(LOG_FILE, "r") as f:
    for line in follow(f):
        check_line(line)