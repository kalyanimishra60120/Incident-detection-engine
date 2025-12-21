import httpx
import uvicorn
from multiprocessing import Process
import time

def run_app():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, log_level="error")

def test_health():
    p = Process(target=run_app, daemon=True)
    p.start()
    try:
        time.sleep(1)
        r = httpx.get("http://127.0.0.1:8002/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
    finally:
        p.terminate()
        p.join()
