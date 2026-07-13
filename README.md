# 🛡 Intrusion Detection System

A containerized, real-time brute-force detection and response pipeline — built to simulate, detect, and automatically respond to login-based attacks.

## What it does

This project simulates a realistic attack scenario end-to-end:

1. **Target** — a Flask login service that logs every attempt (timestamp, IP, username, result)
2. **Attacker** — an automated script simulating a brute-force attack against the target
3. **Guard** — a real-time log-watching detector that identifies suspicious patterns (5+ failed logins from one IP within 30 seconds)
4. **Response** — on detection, the system automatically:
   - Blocks the offending IP at the application layer
   - Sends an email alert to the admin
   - Generates an AI-written incident summary (via Hugging Face's hosted inference API)
5. **Dashboard** — a live, auto-refreshing web dashboard showing attempts, blocked IPs, and stats in real time

All 4 components run as independent, containerized services communicating over Docker's internal network.

## Architecture
┌──────────┐      ┌──────────┐      ┌──────────┐
│ Attacker │ ───> │  Target  │ <─── │Dashboard │
└──────────┘      └────┬─────┘      └──────────┘
│ (shared log volume)
┌────▼─────┐
│  Guard   │ ──> Email + AI Summary + IP Block
└──────────┘

## Tech stack

- **Python / Flask** — target login service, dashboard backend
- **Docker & Docker Compose** — containerization and service orchestration
- **SMTP (Gmail)** — automated email alerting
- **Hugging Face Inference API** — AI-generated incident summaries
- **HTML/CSS/JS** — live auto-refreshing dashboard frontend

## Running it locally

1. Clone this repository
2. Create a `.env` file in the root directory (see `.env.example` for the required format)
3. Run:
docker compose up --build
4. Open the dashboard at `http://127.0.0.1:5001`
5. Watch the attacker automatically simulate a brute-force attack, and observe detection, blocking, email alerts, and AI summaries in the terminal and dashboard in real time

## Key design decisions

- **Application-layer IP blocking** rather than firewall-level (`iptables`) blocking — chosen for portability across environments and to demonstrate detection logic clearly, similar to how many real-world rate-limiting systems work.
- **Shared Docker volume** between `target` and `guard` — allows the detector to read live log data without needing a database or message queue, keeping the architecture simple and easy to reason about.
- **Graceful degradation** — if the AI summary service is unreachable (e.g., network/DNS restrictions), the system falls back to a clean template-based summary instead of failing silently or crashing. Real systems must handle unreachable external dependencies gracefully.

## Known limitations

- The dashboard currently has no authentication — acceptable for local development, but a production deployment would require adding auth before exposing it beyond `localhost`.
- AI-generated summaries depend on reachability of Hugging Face's inference API; in networks that restrict this domain, the system automatically falls back to a template-based summary.
- Detection thresholds (5 failed attempts / 30 seconds) are hardcoded for demonstration; a production system would make these configurable per environment.

## What I learned building this

- Docker networking fundamentals (service-to-service communication, DNS resolution inside containers, volume mounts for shared state)
- Real debugging of production-style issues: output buffering, container startup race conditions, DNS resolution failures, and Docker layer caching
- Designing a detection → response pipeline: not just identifying threats, but acting on them (blocking, alerting, summarizing)