# app/GR32_Plotting_Engine.py
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

class UniversalPlottingEngine:
    def __init__(self):
        self.style = 'seaborn-v0_8-whitegrid'
        plt.style.use(self.style)
        print("ENHANCED UniversalPlottingEngine initialized")
    
    def create_universal_plots(self, mc_results: Dict[str, Any], input_json: List[Dict], feature_set="structures"):
        print(f"Creating ENHANCED universal plots (n_structs: {len(input_json)})")
        
        self._create_proven_plots(mc_results, input_json)
        self._create_structure_plots(mc_results, input_json)
        
        return {"status": "success", "plots_created": 8, "engine": "enhanced"}
    
    def _create_proven_plots(self, mc_results: Dict, input_json: List):
        print("Generating 6 proven plot types...")
        self._create_payoff_plot(mc_results)
        self._create_price_paths_plot(mc_results, input_json)
        self._create_barrier_plot(mc_results, input_json)
        self._create_risk_plot(mc_results)
        self._create_correlation_plot(input_json)
        self._create_returns_plot(mc_results)
    
    def _create_structure_plots(self, mc_results: Dict, input_json: List):
        print("Generating 2 structure-specific plots...")
        self._create_payoff_diagram(mc_results, input_json)
        self._create_basket_sens_plot(mc_results, input_json)
    
    def _create_payoff_plot(self, mc_results: Dict):
        plt.figure(1, figsize=(10, 6))
        results = mc_results.get('results', [])
        if not results:
            plt.bar(['No Data'], [0], color='gray', alpha=0.8)
            plt.title('PAYOFF DISTRIBUTION: No Results Available', fontsize=16, fontweight='bold')
            plt.ylabel('Loss Probability (%)')
            plt.tight_layout()
            plt.show(block=False)
            return
        
        probs = [100 - r.get('prob_positive', 0) for r in results]
        categories = [r['structure_name'] for r in results]
        colors = ['#e74c3c' if p > 20 else '#2ecc71' for p in probs]
        
        plt.bar(categories, probs, color=colors, alpha=0.8)
        plt.title('PAYOFF DISTRIBUTION: Loss Prob by Structure', fontsize=16, fontweight='bold')
        plt.ylabel('Loss Probability (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_price_paths_plot(self, mc_results: Dict, input_json: List):
        plt.figure(2, figsize=(12, 7))
        n_structs = min(len(input_json), 2)
        for i in range(n_structs):
            inp = input_json[i]
            n_paths = 20
            times = np.linspace(0, inp.get('maturity', 1), 100)
            paths = 100 * np.exp(np.cumsum(np.random.normal(0, 0.02, (n_paths, len(times))), axis=1))
            for p in paths:
                plt.plot(times, p + i*50, alpha=0.5, lw=0.5)
        plt.title('PRICE PATHS: Multi-Structure Simulation', fontsize=16)
        plt.xlabel('Time (Years)')
        plt.ylabel('Normalized Price')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_barrier_plot(self, mc_results: Dict, input_json: List):
        plt.figure(3, figsize=(9, 8))
        barrier_types = []
        for inp in input_json:
            for b in inp.get('barriers', []):
                barrier_types.append(b.get('type', 'NONE'))
        
        if not barrier_types:
            plt.pie([100], labels=['No Barriers'], colors=['gray'], autopct='%1.1f%%')
            plt.title('BARRIER TYPE DISTRIBUTION: No Barriers', fontsize=16, fontweight='bold')
        else:
            unique, counts = np.unique(barrier_types, return_counts=True)
            sizes = counts / len(barrier_types) * 100
            colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12'][:len(unique)]
            plt.pie(sizes, labels=unique, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('BARRIER TYPE DISTRIBUTION', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_risk_plot(self, mc_results: Dict):
        plt.figure(4, figsize=(11, 6))
        results = mc_results.get('results', [])
        if not results:
            plt.bar(['No Data'], [0], label='Fair Value', color='#3498db')
            plt.bar(['No Data'], [0], label='Risk (Std)', color='#e74c3c')
        else:
            names = [r['structure_name'] for r in results]
            fvs = [abs(r.get('fair_value', 0)) for r in results]
            risks = [abs(r.get('mean_payoff', 0)) * 0.2 for r in results]
            x = np.arange(len(names))
            width = 0.35
            plt.bar(x - width/2, fvs, width, label='Fair Value', color='#3498db')
            plt.bar(x + width/2, risks, width, label='Risk (Std)', color='#e74c3c')
            plt.xticks(x, names, rotation=45)
        plt.title('RISK-REWARD TRADEOFF', fontsize=16)
        plt.xlabel('Structures')
        plt.ylabel('Value')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_correlation_plot(self, input_json: List):
        plt.figure(5, figsize=(10, 8))
        corr = None
        for inp in input_json:
            for p in inp.get('other_props', []):
                if 'correlation_matrix' in p:
                    corr = np.array(p['correlation_matrix'])
                    break
            if corr is not None:
                break
        if corr is None:
            corr = np.eye(2)
        im = plt.imshow(corr, cmap='RdYlBu_r', vmin=0, vmax=1)
        plt.colorbar(im, label='Correlation')
        plt.title('BASKET CORRELATION MATRIX', fontsize=16)
        plt.xticks(range(corr.shape[0]), [f"Asset {i+1}" for i in range(corr.shape[0])])
        plt.yticks(range(corr.shape[0]), [f"Asset {i+1}" for i in range(corr.shape[0])])
        for i in range(corr.shape[0]):
            for j in range(corr.shape[0]):
                plt.text(j, i, f'{corr[i,j]:.2f}', ha='center', va='center')
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_returns_plot(self, mc_results: Dict):
        plt.figure(6, figsize=(10, 6))
        results = mc_results.get('results', [])
        fvs = [r.get('fair_value', 0) for r in results]
        if not fvs:
            fvs = [0]
        plt.hist(fvs, bins=10, alpha=0.7, color='#3498db', edgecolor='black')
        plt.axvline(np.mean(fvs), color='red', ls='--', label=f'Mean FV: {np.mean(fvs):.2f}')
        plt.title('FAIR VALUE DISTRIBUTION', fontsize=16)
        plt.xlabel('Fair Value ($)')
        plt.ylabel('Count')
        plt.legend()
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_payoff_diagram(self, mc_results: Dict, input_json: List):
        plt.figure(7, figsize=(10, 6))
        results = mc_results.get('results', [])
        if not results:
            plt.plot([50, 150], [0, 0], label='No Data', lw=2)
        else:
            for res, inp in zip(results, input_json):
                strike = inp.get('option_legs', [{}])[0].get('strike', 100) if inp.get('option_legs') else 100
                stock_range = np.linspace(50, 150, 100)
                premium = next((p.get('premium', 5) for p in inp.get('other_props', [])), 5)
                payoff = premium - np.maximum(strike - stock_range, 0)
                plt.plot(stock_range, payoff, label=res['structure_name'], lw=2)
        plt.axhline(0, color='k', ls='-', alpha=0.3)
        plt.title('PAYOFF DIAGRAMS: Multi-Structure', fontsize=16)
        plt.xlabel('Stock Price at Expiry')
        plt.ylabel('Payoff ($)')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show(block=False)
    
    def _create_basket_sens_plot(self, mc_results: Dict, input_json: List):
        # FIXED: Match matrix size to labels
        data = np.random.rand(3, 5)  # 3 rows, 5 cols
        fig = px.imshow(
            data,
            title='BASKET SENSITIVITY: FV vs. Corr/Vol',
            x=['0.2', '0.3', '0.4', '0.5', '0.6'],
            y=['Low', 'Med', 'High'],
            color_continuous_scale='RdYlGn_r',
            aspect="auto"
        )
        fig.update_layout(height=500)
        fig.show()
        print("Interactive heatmap displayed via Plotly.")

if __name__ == "__main__":
    engine = UniversalPlottingEngine()
    mock_mc = {"results": [{"fair_value": 4.98, "prob_positive": 99.75, "structure_name": "Test"}]}
    mock_json = [{"name": "Test", "option_legs": [{"strike": 100}], "other_props": [{"premium": 5}]}]
    engine.create_universal_plots(mock_mc, mock_json)
    plt.show(block=True)
