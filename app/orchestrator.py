import os
from datetime import datetime
from typing import Dict, Any, List
from app.scanner import parse_deal
from app.GR21_MC_Engine import Structure, mc_value
from app.GR31_Report_Engine import ReportEngine
from app.GR32_Plotting_Engine import UniversalPlottingEngine

class UScanOrchestrator:
    def __init__(self):
        self.report_engine = ReportEngine()
        self.plot_engine = UniversalPlottingEngine()

    def _to_gr21_input(self, parsed: Dict) -> List[Dict]:
        underlyings = parsed.get("basket", ["Tencent", "Baba"])
        initial_prices = [100.0] * len(underlyings)
        barriers = []
        if parsed.get("ko", 0) > 0:
            barriers.append({"type": "KO_DOWN", "level": f"{parsed['ko']}%"})
        props = [
            {"principal": parsed.get("principal", 100)},
            {"coupon": parsed.get("coupon", 0)}
        ]
        return [{
            "name": parsed.get("name", "Structured Note"),
            "underlyings": underlyings,
            "initial_prices": initial_prices,
            "maturity": parsed.get("maturity_months", 4) / 12.0,
            "basket_type": "WORST_OF",
            "barriers": barriers,
            "other_props": props
        }]

    def _run_mc(self, gr21_input: List[Dict]) -> Dict:
        results = []
        for s in gr21_input:
            struct = Structure.from_json(s)
            mc = mc_value(struct, n_paths=10000, n_steps=1)
            mc["structure_name"] = struct.name
            results.append(mc)
        return {"results": results, "datetime": datetime.now().isoformat()}

def run_analysis(text: str, user_id: str = "guest") -> Dict:
    orch = UScanOrchestrator()
    parsed = parse_deal(text)
    if not parsed:
        return {"status": "error", "error": "Failed to parse deal"}
    gr21_input = orch._to_gr21_input(parsed)
    mc_results = orch._run_mc(gr21_input)
    report = orch.report_engine.generate_report(mc_results, gr21_input)
    plots = orch.plot_engine.create_universal_plots(mc_results, gr21_input)
    result = {
        "status": "success",
        "parsed": parsed,
        "mc": mc_results,
        "report": report,
        "plots": plots
    }
    # Save outputs
    os.makedirs(f"outputs/{user_id}", exist_ok=True)
    base = f"outputs/{user_id}/USCAN_{datetime.now().strftime('%Y%m%d_%H%M')}"
    import json
    with open(f"{base}.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    with open(f"{base}_Report.md", "w") as f:
        f.write(result["report"]["markdown"])
    return result
