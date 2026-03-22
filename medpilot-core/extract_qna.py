import json
import sys
import os

sys.path.insert(0, r"d:\Downloads\antigravity_prj\MedAI\medpilot-core")

# Mock the database init to prevent issues when importing main
import app.db as db
db.init_db = lambda: None

import app.main as main

data = {
    "patient_qna": main.PATIENT_QNA,
    "default_patient_answer": main.DEFAULT_PATIENT_ANSWER
}

os.makedirs(r"d:\Downloads\antigravity_prj\MedAI\medpilot-core\data", exist_ok=True)
with open(r"d:\Downloads\antigravity_prj\MedAI\medpilot-core\data\qna_demo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("QnA data extracted successfully.")
