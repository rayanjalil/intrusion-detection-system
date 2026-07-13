from flask import Flask, request
from datetime import datetime
import os

app = Flask(__name__)

CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "password123"
BLOCKED_FILE = "blocked_ips.txt"

def log_attempt(ip, username, success):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = "SUCCESS" if success else "FAIL"
    with open("attempts.log", "a") as f:
        f.write(f"{timestamp},{ip},{username},{result}\n")

def is_blocked(ip):
    if not os.path.exists(BLOCKED_FILE):
        return False
    with open(BLOCKED_FILE, "r") as f:
        blocked_ips = set(line.strip() for line in f)
    return ip in blocked_ips

@app.route('/login', methods=['POST'])
def login():
    ip = request.remote_addr

    if is_blocked(ip):
        return "Forbidden: your IP has been blocked due to suspicious activity", 403

    username = request.form.get('username')
    password = request.form.get('password')

    if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        log_attempt(ip, username, True)
        return "Login successful", 200
    else:
        log_attempt(ip, username, False)
        return "Login failed", 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)