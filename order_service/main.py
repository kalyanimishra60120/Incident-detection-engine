from fastapi import FastAPI
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import uuid
import random
import os

os.makedirs("/app/logs", exist_ok=True)

logger = logging.getLogger("order-service")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("/app/logs/order.log", maxBytes=2_000_000, backupCount=3)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s %(service)s %(event)s %(request_id)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

def rid():
    return str(uuid.uuid4())

@app.post("/order")
def create_order():
    # simulate intermittent failure (realistic)
    if random.randint(1, 4) == 4:
        logger.error(
            "order_failed",
            extra={
                "service": "order-service",
                "event": "order_failed",
                "request_id": rid()
            }
        )
        return {"status": "error"}

    logger.info(
        "order_created",
        extra={
            "service": "order-service",
            "event": "order_created",
            "request_id": rid()
        }
    )
    return {"status": "created"}
