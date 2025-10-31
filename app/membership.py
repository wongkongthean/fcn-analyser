# app/membership.py
from enum import Enum
from datetime import datetime
import json
import os

class MembershipTier(Enum):
    FREE = "free"
    PREMIUM = "premium"

class UScanMembership:
    def __init__(self):
        self.db_path = "data/user_usage.json"
        os.makedirs("data", exist_ok=True)
        self._ensure_db()

    def _ensure_db(self):
        """Create valid JSON file if missing or corrupt"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({}, f)
            print(f"Created new user DB: {self.db_path}")
            return
        
        # Validate JSON
        try:
            with open(self.db_path, "r") as f:
                json.load(f)
        except:
            print(f"Corrupted DB detected. Resetting {self.db_path}")
            with open(self.db_path, "w") as f:
                json.dump({}, f)

    def can_run_analysis(self, user_id: str) -> dict:
        self._ensure_db()
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
        except:
            data = {}
        
        if user_id not in data:
            data[user_id] = {"tier": "free", "runs": {}, "created": datetime.now().isoformat()}
        
        user = data[user_id]
        month = datetime.now().strftime("%Y-%m")
        runs = user["runs"].get(month, 0)
        
        if user["tier"] == "free" and runs >= 5:
            return {"allowed": False, "remaining": 0, "message": "Free tier limit: 5/month. Upgrade?"}
        
        user["runs"][month] = runs + 1
        data[user_id] = user
        
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)
        
        remaining = "Unlimited" if user["tier"] == "premium" else max(0, 5 - runs - 1)
        return {"allowed": True, "remaining": remaining, "message": f"Run #{runs + 1}"}

# Legal Disclaimers
LEGAL_DISCLAIMERS = {
    "educational": """
## Educational Purpose Only
USCAN is an **educational tool** for learning about structured products. 
**This is not financial advice.**
""",
    "no_liability": """
## No Liability
We are **not responsible** for any financial decisions or losses.
**Use at your own risk.**
"""
}
