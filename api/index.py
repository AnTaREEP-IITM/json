from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Example telemetry data (replace with your downloaded bundle)
telemetry_data = [
    {"region": "emea", "latency_ms": 170, "uptime": 0.99},
    {"region": "emea", "latency_ms": 180, "uptime": 0.98},
    {"region": "amer", "latency_ms": 190, "uptime": 0.97},
    {"region": "amer", "latency_ms": 175, "uptime": 0.95},
]

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/")
async def get_metrics(body: RequestBody):
    response = {}
    for region in body.regions:
        data = [r for r in telemetry_data if r["region"] == region]
        if not data:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": None
            }
            continue
        latencies = [r["latency_ms"] for r in data]
        uptimes = [r["uptime"] for r in data]
        breaches = sum(1 for l in latencies if l > body.threshold_ms)

        response[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches
        }
    return response
