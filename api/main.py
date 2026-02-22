# api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json
from pathlib import Path

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Load telemetry JSON once at startup
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "telemetry.json") as f:
    telemetry_data = json.load(f)

@app.post("/api/latency")
async def compute_metrics(req: Request):
    try:
        body = await req.json()
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)

        response = {}
        for region in regions:
            region_data = [r for r in telemetry_data if r["region"] == region]
            if not region_data:
                response[region] = {
                    "avg_latency": None,
                    "p95_latency": None,
                    "avg_uptime": None,
                    "breaches": 0
                }
                continue

            latencies = [r["latency_ms"] for r in region_data]
            uptimes = [r["uptime_pct"] for r in region_data]
            breaches = sum(1 for r in region_data if r["latency_ms"] > threshold)

            response[region] = {
                "avg_latency": float(np.mean(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": float(np.mean(uptimes)),
                "breaches": breaches
            }

        return JSONResponse(content=response)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
