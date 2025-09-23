from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()
tok = AutoTokenizer.from_pretrained("./")
model = AutoModelForCausalLM.from_pretrained("./")
model = model.to("cuda" if torch.cuda.is_available() else "cpu")

class Payload(BaseModel):
    legend: str
    role: str
    principles: List[str]
    evidence: Dict[str, Any]

@app.post("/score")
def score(p: Payload):
    # Minimal deterministic placeholder; replace with proper prompting of the LoRA-adapted model
    labels = ["Invest", "Pass", "Strong", "Weak"]
    decision_scores = {lbl: 0.5 for lbl in labels}
    decision_scores["Invest"] = 0.7 if "moat" in " ".join(p.principles) else 0.3
    return {"decision_scores": decision_scores, "applied_principles": p.principles[:3]}
