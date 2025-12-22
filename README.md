## Incident Detection Engine (Dockerized)
## Overview
The Incident Detection Engine is a Dockerized, multi-service system that detects real operational incidents by analyzing application logs over time instead of reacting to individual errors. Rather than alerting on every failure, the system applies frequency-based and time-window-based logic to determine when a service is genuinely unstable, opens a single incident, tracks its lifecycle, and automatically resolves it when the system stabilizes.This project demonstrates core DevOps / SRE observability and incident-management principles without relying on heavy external monitoring stacks.

## Problem Statement
In real production environments:
Applications generate large volumes of logs
Single errors are common and often harmless
Alerting on every error leads to alert fatigue
Engineers begin ignoring alerts
Real outages are detected late or missed entirely
The key challenge is separating noise from signal.
This project addresses that challenge by detecting patterns of failure, not individual failures.

## What This Project Does
At a high level, the system:
Runs multiple backend services that generate structured logs
Continuously monitors those logs in real time
Detects incidents only when error frequency crosses defined thresholds
Deduplicates alerts so only one incident per failure pattern is created
Tracks the full incident lifecycle:
----OPEN → ONGOING → RESOLVED-----
Automatically resolves incidents after a configurable cooldown period
All components run together inside Docker, simulating a realistic production setup.

## Internal Working (How Everything Connects)
## 1. Services Generate Logs
Two independent FastAPI services run:
auth-service (port 8000) , order-service (port 8001)
Each service writes structured logs to its own log file : app.log, order.log
Services do not communicate with the incident engine directly
Logs act as the single source of truth

## 2. Incident Engine Tails Logs in Real Time
The incident engine continuously tails all service log files (similar to tail -f)
Only new log entries are processed
No polling, no API calls, no tight coupling

## 3. Pattern Matching and Sliding Windows
Detection rules are defined in incident_config.json
For each configured pattern:
-Matching log entries are timestamped
-A sliding time window is maintained in memory
-Old events outside the window are discarded automatically
This ensures:
-Isolated errors are ignored
-Rapid error bursts are detected

## 4. Incident Qualification
An incident is opened only when: Error count ≥ threshold
All errors occur within the configured time window
When this happens:A unique incident ID is generated
Severity, service name, and timestamps are recorded

The incident is marked OPEN

Details are written to incidents.log

Duplicate incidents for the same service + pattern are suppressed.

5. Incident Resolution

While errors continue, the incident remains open

When no new matching errors occur for the cooldown period:

The incident is marked RESOLVED

Duration is calculated

Resolution is logged

This completes the incident lifecycle.


