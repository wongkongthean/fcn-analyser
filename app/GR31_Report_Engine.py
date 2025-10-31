import datetime
from typing import Dict, List

class ReportEngine:
    def __init__(self):
        pass

    def generate_report(self, mc_results: Dict, gr21_input: List[Dict]) -> Dict:
        results = mc_results["results"]
        report_lines = ["# USCAN Structured Product Report\n"]
        report_lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Structures Analyzed:** {len(results)}")
        
        # Use GROSS fair value
        avg_fv = sum(r["fair_value_gross"] for r in results) / len(results)
        report_lines.append(f"**Average Fair Value:** ${avg_fv:.2f}\n")
        report_lines.append("This report provides a comprehensive analysis of the structured product(s) based on Monte Carlo simulations and AI-parsed inputs.\n")

        report_lines.append("## Assumptions\n")
        for s, r in zip(gr21_input, results):
            struct_name = s["name"]
            underlyings = ", ".join(s["underlyings"])
            maturity = s["maturity"]
            ko_level = next((b["level"] for b in s["barriers"] if b["type"] == "KO_DOWN"), "100%")
            report_lines.append(f"- **{struct_name}**: {underlyings}, {maturity:.2f} years, WORST_OF, Barriers: KO_DOWN at {ko_level}")

        report_lines.append("\n## Results\n")
        for s, r in zip(gr21_input, results):
            struct_name = s["name"]
            fv = r["fair_value_gross"]
            prob = r["prob_no_ko"]
            report_lines.append(f"- **{struct_name}**: Fair Value = ${fv:.2f}, Survival Probability = {prob:.2f}%")

        report_lines.append("\n## Recommendations\n")
        for s, r in zip(gr21_input, results):
            struct_name = s["name"]
            prob = r["prob_no_ko"]
            if prob > 70:
                report_lines.append(f"- **{struct_name}**: High survival ({prob:.1f}%). Attractive if priced near fair value.")
            elif prob > 50:
                report_lines.append(f"- **{struct_name}**: Moderate risk ({100-prob:.1f}% KO). Consider if coupon justifies.")
            else:
                report_lines.append(f"- **{struct_name}**: High KO risk ({100-prob:.1f}%). Only for risk-tolerant investors.")

        markdown = "\n".join(report_lines)
        return {"markdown": markdown}
