from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def healthcheck():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/metrics")
def metrics():
    return {
        "analysis_count_total": 0,
        "queue_depth": 0,
        "model_versions": {
            "ruleset": "rules-v0.1.0",
            "tabular_model": "demo-xgb-v0.1.0",
        },
    }
