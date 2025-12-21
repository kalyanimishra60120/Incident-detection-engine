from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import uuid
import os

# Ensure log directory exists
os.makedirs("/app/logs", exist_ok=True)

LOG_FILE = "/app/logs/app.log"

# Configure JSON Logger
logger = logging.getLogger("logmon")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3, encoding="utf-8")
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(service)s %(event)s %(request_id)s')
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)

app = FastAPI()

def new_request_id():
    return str(uuid.uuid4())

@app.get("/health")
async def health():
    logger.info("health_check", extra={"service":"logmon", "event":"health", "request_id": new_request_id()})
    return {"status": "ok"}

@app.get("/error")
async def error_endpoint():
    try:
        raise ValueError("Simulated error for alert testing")
    except Exception as e:
        logger.error("error_event", extra={"service":"logmon", "event":"error", "detail": str(e), "request_id": new_request_id()})
        return JSONResponse({"error": "simulated error"}, status_code=500)

@app.post("/login")
async def login(payload: dict):
    username = payload.get("username")
    password = payload.get("password")
    rid = new_request_id()

    if username == "admin" and password == "password":
        logger.info("login_success", extra={"service":"logmon","event":"login_success","username":username,"request_id":rid})
        return {"status":"ok"}

    logger.warning("login_failed", extra={"service":"logmon","event":"login_failed","username":username,"request_id":rid})
    raise HTTPException(status_code=401, detail="Invalid credentials")

