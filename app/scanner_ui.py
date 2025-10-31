import streamlit as st
import os
import json
import traceback
from datetime import datetime
import numpy as np
import re

# === parse_deal (INLINE) ===
def parse_deal(text: str):
    try:
        text = text.lower().replace(" p.a.", "").replace(" coupon", "").replace(" ko ", " ko")
        months = int(re.search(r"(\d+)\s*months?", text).group(1))
        basket = [w.capitalize() for w in re.findall(r"tencent|baba|hsbc|meta", text)]
        ko_match = re.search(r"ko\s*(\d+)%?", text)
        ko = int(ko_match.group(1)) if ko_match else 0
        coupon_match = re.search(r"(\d+(?:\.\d+)?)%", text)
        coupon = float(coupon_match.group(1)) if coupon_match else 0
        name = f"{'_'.join(basket)}_KO{ko}"
        return {
            "name": name,
            "basket": basket,
            "maturity_months": months,
            "ko": ko,
            "coupon": coupon,
            "principal": 100
        }
    except Exception as e:
        st.error(f"Parse error: {e}")
        return None

# === Structure & mc_value (INLINE) ===
def mc_value(struct, n_paths=10000, n_steps=1):
    np.random.seed(42)
    T = struct["maturity"]
    S0 = struct["initial_prices"]
    n = len(S0)
    dt = T / n_steps
    drift = (0.05 - 0.5 * 0.2**2) * dt
    vol = 0.2 * np.sqrt(dt)
    paths = np.exp(np.cumsum(drift + vol * np.random.randn(n_paths, n_steps, n), axis=1)) * np.array(S0)
    paths = np.concatenate([np.array(S0)[None, :], paths], axis=1)
    worst = np.min(paths, axis=2)
    ko_level = 0.98
    ko_hit = np.any(worst <= ko_level, axis=1)
    survival = ~ko_hit
    coupon = struct["other_props"][1]["coupon"]
    payoff = np.where(survival, 100 + coupon * T * 100, 
                      np.where(worst[:, -1] < ko_level, worst[:, -1] * 100, 100))
    fv = np.mean(payoff) * np.exp(-0.05 * T)
    prob_no_ko = np.mean(survival)
    return {
        "fair_value_gross": round(fv, 2),
        "prob_no_ko": round(prob_no_ko * 100, 2)
    }

# === ReportEngine (INLINE) ===
class ReportEngine:
    def generate_report(self, mc_results, gr21_input):
        mc = mc_results["results"][0]
        s = gr21_input[0]
        fv = mc["fair_value_gross"]
        ko_risk = 100 - mc["prob_no_ko"]
        markdown = f"""
# USCAN Report
**{datetime.now().strftime('%Y-%m-%d %H:%M')}**

## Deal
- **Name**: {s['name']}
- **Basket**: {', '.join(s['underlyings'])}
- **Maturity**: {s['maturity']:.2f} years
- **KO**: {s['barriers'][0]['level'] if s['barriers'] else 'None'}

## Valuation
- **Fair Value**: ${fv:.2f}
- **Overpriced by**: ${100 - fv:.2f}
- **KO Risk**: {ko_risk:.1f}%

## Verdict
{"**AVOID** — High KO risk" if ko_risk > 60 else "**CONSIDER** — Fair pricing"}
"""
        return {"markdown": markdown.strip()}

# === run_analysis (ALL IN ONE) ===
def run_analysis(text: str, user_id: str = "guest"):
    try:
        st.write("**1/4** Parsing...")
        parsed = parse_deal(text)
        if not parsed:
            return {"status": "error", "error": "Parse failed"}

        st.write("**2/4** Building model...")
        gr21_input = [{
            "name": parsed["name"],
            "underlyings": parsed["basket"],
            "initial_prices": [100.0] * len(parsed["basket"]),
            "maturity": parsed["maturity_months"] / 12.0,
            "basket_type": "WORST_OF",
            "barriers": [{"type": "KO_DOWN", "level": f"{parsed['ko']}%"}] if parsed["ko"] else [],
            "other_props": [{"principal": 100}, {"coupon": parsed["coupon"] / 100}]
        }]

        st.write("**3/4** Monte Carlo (10k paths)...")
        results = []
        mc = mc_value(gr21_input[0], n_paths=10000)
        mc["structure_name"] = gr21_input[0]["name"]
        results.append(mc)
        mc_results = {"results": results}

        st.write("**4/4** Report...")
        engine = ReportEngine()
        report = engine.generate_report(mc_results, gr21_input)

        # Save
        os.makedirs(f"outputs/{user_id}", exist_ok=True)
        base = f"outputs/{user_id}/USCAN_{datetime.now().strftime('%Y%m%d_%H%M')}"
        with open(f"{base}.json", "w") as f:
            json.dump({"mc": mc_results, "report": report}, f, indent=2, default=str)
        with open(f"{base}_Report.md", "w") as f:
            f.write(report["markdown"])

        return {"status": "success", "mc": mc_results, "report": report}
    except Exception as e:
        tb = traceback.format_exc()
        st.error(f"**CRASH**: {e}")
        st.code(tb)
        return {"status": "error", "error": str(e), "traceback": tb}

# === UI ===
st.set_page_config(page_title="USCAN", layout="centered")
st.title("USCAN — The Truth Engine")
st.caption("No illusions. Just math.")

text = st.text_area(
    "Deal Description",
    value="4 months Tencent + Baba KO 98% 11% coupon p.a. GS",
    height=100
)

if st.button("Analyze", type="primary"):
    with st.spinner("Running full analysis..."):
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
        st.error("Analysis failed.")
