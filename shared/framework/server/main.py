import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from dotenv import load_dotenv
from .config_loader import load_principles, load_decision_tree, load_adapters
from .decision_engine import DecisionEngine

load_dotenv()

app = FastAPI(title="Business Infinity Orchestrator")

principles = load_principles()
tree = load_decision_tree()
adapters = load_adapters()
engine = DecisionEngine(tree, adapters, principles)

class Evidence(BaseModel):
    data: dict

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/decisions/run")
def run_decision(evidence: Evidence):
    return engine.run(evidence.data)

@app.post("/adapters/switch")
def switch_adapter(payload: dict = Body(...)):
    # No-op placeholder; adapter registry could be mutable and persisted
    return {"status": "ack", "requested": payload}
