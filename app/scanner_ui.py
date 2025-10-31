import streamlit as st
import traceback

try:
    from app.orchestrator import run_analysis
    print("IMPORT SUCCESS: run_analysis loaded")
except Exception as e:
    print("IMPORT ERROR:", e)
    traceback.print_exc()

st.title("USCAN — Structured Product Pricer")
st.write("Paste deal text below (e.g. `4 months Tencent + Baba KO 98% 11% coupon p.a. GS`)")

text = st.text_area("Deal Description", height=100)
if st.button("Analyze"):
    with st.spinner("Running Monte Carlo..."):
        result = run_analysis(text)
    if result["status"] == "success":
        mc = result["mc"]["results"][0]
        fv = mc["fair_value_gross"]
        overpriced = 100 - fv
        ko_risk = 100 - mc["prob_no_ko"]
        st.success(f"Fair Value: ${fv:.2f}")
        st.warning(f"Overpriced by: ${overpriced:.2f} | KO Risk: {ko_risk:.1f}%")
        st.markdown(result["report"]["markdown"])
    else:
        st.error(result["error"])
