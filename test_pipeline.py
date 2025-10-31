from app.orchestrator import UScanOrchestrator

deal = {
    "name": "Tencent_Baba_KO98",
    "basket": ["Tencent", "Baba"],
    "maturity_months": 4,
    "ko": 98,
    "coupon": 11,
    "principal": 100
}

print("USCAN STRUCTURED NOTE - REAL MARKET PRICING")
orch = UScanOrchestrator()
inp = orch._to_gr21_input(deal)
mc = orch._run_mc(inp)["results"][0]

fv = mc["fair_value_gross"]
overpriced = 100 - fv
ko_risk = 100 - mc["prob_no_ko"]

print(f"Principal Invested: ${deal['principal']:.2f}")
print(f"Fair Value of Note: ${fv:.2f}")
print(f"Overpriced by: ${overpriced:.2f}")
print(f"KO Risk: {ko_risk:.1f}%")
print(f"Expected Return if No KO: +{11 * 4/12:.2f}%")
