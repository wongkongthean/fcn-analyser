from app.scanner import parse_deal
from app.GR21_MC_Engine import Structure, mc_value
from app.GR31_Report_Engine import ReportEngine
import os
import json
from datetime import datetime

class UScanOrchestrator:
    def __init__(self):
        self.report_engine = ReportEngine()

    def _to_gr21_input(self, parsed):
        underlyings = parsed.get("basket", ["Tencent", "Baba"])
        initial_prices = [100.0] * len(underlyings)
        barriers = []
        if parsed.get("ko"):
            barriers.append({"type": "KO_DOWN", "level": f"{parsed['ko']}%"})
        props = [
            {"principal": parsed.get("principal", 100)},
            {"coupon": parsed.get("coupon", 0)}
        ]
        return [{
            "name": parsed.get("name", "Note"),
            "underlyings": underlyings,
            "initial_prices": initial_prices,
            "maturity": parsed.get("maturity_months", 4) / 12.0,
            "basket_type": "WORST_OF",
            "barriers": barriers,
            "other_props": props
        }]

    def _run_mc(self, gr21_input):
        results = []
        for s in gr21_input:
            struct = Structure.from_json(s)
            mc = mc_value(struct, n_paths=10000, n_steps=1)
            mc["structure_name"] = struct.name
            results.append(mc)
        return {"results": results}

def run_analysis(text: str, user_id: str = "guest"):
    orch = UScanOrchestrator()
    parsed = parse_deal(text)
    if not parsed:
        return {"status": "error", "error": "Parse failed"}
    gr21 = orch._to_gr21_input(parsed)
    mc = orch._run_mc(gr21)
    report = orch.report_engine.generate_report(mc, gr21)
    os.makedirs(f"outputs/{user_id}", exist_ok=True)
    base = f"outputs/{user_id}/USCAN_{datetime.now().strftime('%Y%m%d_%H%M')}"
    with open(f"{base}.json", "w") as f:
        json.dump({"mc": mc, "report": report}, f, indent=2, default=str)
    with open(f"{base}_Report.md", "w") as f:
        f.write(report["markdown"])
    return {
        "status": "success",
        "mc": mc,
        "report": report
    }
