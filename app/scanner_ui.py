import streamlit as st
import os
import json
import traceback
from datetime import datetime

# === FULL run_analysis FUNCTION (EMBEDDED) ===
def run_analysis(text: str, user_id: str = "guest"):
    try:
        st.write("Parsing deal...")
        from app.scanner import parse_deal
        parsed = parse_deal(text)
        if not parsed:
            return {"status": "error", "error": "Failed to parse deal text"}

        st.write(f"Parsed: {parsed}")

        # Build GR21 input
        underlyings = parsed.get("basket", ["Tencent", "Baba"])
        initial_prices = [100.0] * len(underlyings)
        barriers = []
        if parsed.get("ko"):
            barriers.append({"type": "KO_DOWN", "level": f"{parsed['ko']}%"})
        props = [
            {"principal": parsed.get("principal", 100)},
            {"coupon": parsed.get("coupon", 0)}
        ]
        gr21_input = [{
            "name": parsed.get("name", "Note"),
            "underlyings": underlyings,
            "initial_prices": initial_prices,
            "maturity": parsed.get("maturity_months", 4) / 12.0,
            "basket_type": "WORST_OF",
            "barriers": barriers,
            "other_props": props
        }]

        st.write("Running Monte Carlo...")
        from app.GR21_MC_Engine import Structure, mc_value
        results = []
        for s in gr21_input:
            struct = Structure.from_json(s)
            mc = mc_value(struct, n_paths=10000, n_steps=1)
            mc["structure_name"] = struct.name
            results.append(mc)
        mc_results = {"results": results}

        st.write("Generating report...")
        from app.GR31_Report_Engine import ReportEngine
        report_engine = ReportEngine()
        report = report_engine.generate_report(mc_results, gr21_input)

        # Save outputs
        os.makedirs(f"outputs/{user_id}", exist_ok=True)
        base = f"outputs/{user_id}/USCAN_{datetime.now().strftime('%Y%m%d_%H%M')}"
        with open(f"{base}.json", "w") as f:
            json.dump({"mc": mc_results, "report": report}, f, indent=2, default=str)
        with open(f"{base}_Report.md", "w") as f:
            f.write(report["markdown"])

        return {
            "status": "success",
            "mc": mc_results,
            "report": report
        }
    except Exception as e:
        tb = traceback.format_exc()
        st.error(f"Analysis failed: {e}")
        st.code(tb)
        return {"status": "error", "error": str(e), "traceback": tb}

# === STREAMLIT UI ===
st.set_page_config(page_title="USCAN", layout="centered")
st.title("USCAN — Structured Product Pricer")
st.caption("Paste deal text below (e.g. `4 months Tencent + Baba KO 98% 11% coupon p.a. GS`)")

text = st.text_area("Deal Description", height=100, value="4 months Tencent + Baba KO 98% 11% coupon p.a. GS")

if st.button("Analyze", type="primary"):
    with st.spinner("Analyzing..."):
        result = run_analysis(text)
    if result["status"] == "success":
        mc = result["mc"]["results"][0]
        fv = mc["fair_value_gross"]
        overpriced = 100 - fv
        ko_risk = 100 - mc["prob_no_ko"]
        st.success(f"**Fair Value: ${fv:.2f}**")
        st.warning(f"**Overpriced by: ${overpriced:.2f} | KO Risk: {ko_risk:.1f}%**")
        st.markdown("---")
        st.markdown(result["report"]["markdown"])
    else:
        st.error("Analysis failed. See traceback above.")
