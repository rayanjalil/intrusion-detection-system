from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

ATTEMPTS_FILE = "/data/attempts.log"
BLOCKED_FILE = "/data/blocked_ips.txt"

def read_attempts():
    if not os.path.exists(ATTEMPTS_FILE):
        return []
    attempts = []
    with open(ATTEMPTS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 4:
                continue
            timestamp, ip, username, result = parts
            attempts.append({
                "timestamp": timestamp,
                "ip": ip,
                "username": username,
                "result": result
            })
    return attempts

def read_blocked_ips():
    if not os.path.exists(BLOCKED_FILE):
        return []
    with open(BLOCKED_FILE, "r") as f:
        ips = [line.strip() for line in f if line.strip()]
    return sorted(set(ips))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def stats():
    attempts = read_attempts()
    blocked = read_blocked_ips()
    total = len(attempts)
    failed = len([a for a in attempts if a["result"] == "FAIL"])
    success = len([a for a in attempts if a["result"] == "SUCCESS"])
    return jsonify({
        "total_attempts": total,
        "failed_attempts": failed,
        "successful_logins": success,
        "blocked_count": len(blocked)
    })

@app.route("/api/attempts")
def attempts_api():
    attempts = read_attempts()
    return jsonify(list(reversed(attempts))[:50])

@app.route("/api/blocked")
def blocked_api():
    return jsonify(read_blocked_ips())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)