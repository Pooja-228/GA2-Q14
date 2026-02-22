from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

# Mock telemetry data
telemetry_data = [
    {"region": "emea", "latency_ms": 120, "uptime": 0.99},
    {"region": "emea", "latency_ms": 180, "uptime": 1.0},
    {"region": "amer", "latency_ms": 150, "uptime": 0.98},
    {"region": "amer", "latency_ms": 200, "uptime": 0.97},
    {"region": "apac", "latency_ms": 100, "uptime": 0.995},
]

@app.post("/api/latency")
async def compute_metrics(req: Request):
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
        uptimes = [r["uptime"] for r in region_data]
        breaches = sum(1 for r in region_data if r["latency_ms"] > threshold)

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches
        }

    return JSONResponse(content=response)
