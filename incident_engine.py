import time
import os
import json
from collections import defaultdict, deque
from datetime import datetime

# ==============================
# CONFIGURATION
# ==============================

# Service name -> log file path
LOG_FILES = {
    "auth-service": "/app/logs/app.log",
    "order-service": "/app/logs/order.log"
}

INCIDENT_LOG = "/app/logs/incidents.log"
CONFIG_FILE = "/app/incident_config.json"

# ==============================
# STATE
# ==============================

# key = service:pattern -> deque[timestamps]
event_windows = defaultdict(lambda: deque())

# key = service:pattern -> incident dict
open_incidents = {}

# ==============================
# UTILITIES
# ==============================

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def now():
    return time.time()

def log_block(block: str):
    with open(INCIDENT_LOG, "a", encoding="utf-8") as f:
        f.write(block)
    print(block, flush=True)

def generate_incident_id():
    return f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

# ==============================
# INCIDENT LIFECYCLE
# ==============================

def open_incident(service, pattern, rule, count):
    incident_id = generate_incident_id()

    incident = {
        "id": incident_id,
        "service": service,
        "pattern": pattern,
        "severity": rule["severity"],
        "count": count,
        "start_ts": now(),
        "last_seen": now(),
        "description": rule.get("description", "")
    }

    key = f"{service}:{pattern}"
    open_incidents[key] = incident

    block = (
        "\n=========================================\n"
        "INCIDENT OPENED\n"
        f"ID: {incident_id}\n"
        f"SERVICE: {service}\n"
        f"PATTERN: {pattern}\n"
        f"SEVERITY: {incident['severity']}\n"
        f"EVENT COUNT: {count}\n"
        f"DESCRIPTION: {incident['description']}\n"
        f"START TIME: {datetime.utcnow().isoformat()}\n"
        "=========================================\n"
    )

    log_block(block)

def resolve_incident(key, rule):
    incident = open_incidents.pop(key)
    duration = int(now() - incident["start_ts"])

    block = (
        "\n-----------------------------------------\n"
        "INCIDENT RESOLVED\n"
        f"ID: {incident['id']}\n"
        f"SERVICE: {incident['service']}\n"
        f"PATTERN: {incident['pattern']}\n"
        f"DURATION: {duration} seconds\n"
        f"RESOLVED AT: {datetime.utcnow().isoformat()}\n"
        "-----------------------------------------\n"
    )

    log_block(block)

# ==============================
# MAIN ENGINE
# ==============================

def monitor():
    print("Incident Detection Engine started (multi-service)...", flush=True)

    config = load_config()

    # Open log files
    file_handles = {}

    for service, path in LOG_FILES.items():
        while not os.path.exists(path):
            print(f"Waiting for log file: {path}", flush=True)
            time.sleep(1)

        f = open(path, "r", encoding="utf-8")
        f.seek(0, os.SEEK_END)
        file_handles[service] = f

    while True:
        current_time = now()

        # ------------------------------
        # 1. Process new log lines
        # ------------------------------
        for service, f in file_handles.items():
            line = f.readline()
            if not line:
                continue

            for pattern, rule in config.items():
                if pattern in line:
                    key = f"{service}:{pattern}"

                    window = event_windows[key]
                    window.append(current_time)

                    # Remove events outside time window
                    while window and current_time - window[0] > rule["window_seconds"]:
                        window.popleft()

                    # Open incident if threshold crossed
                    if len(window) >= rule["threshold"] and key not in open_incidents:
                        open_incident(
                            service=service,
                            pattern=pattern,
                            rule=rule,
                            count=len(window)
                        )

                    # Update last seen time
                    if key in open_incidents:
                        open_incidents[key]["last_seen"] = current_time

        # ------------------------------
        # 2. Resolve incidents
        # ------------------------------
        for key, incident in list(open_incidents.items()):
            service, pattern = key.split(":", 1)
            rule = config[pattern]

            if current_time - incident["last_seen"] >= rule["cooldown_seconds"]:
                resolve_incident(key, rule)

        time.sleep(1)

# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    monitor()

