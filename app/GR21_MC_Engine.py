# USCAN — GR21 Monte Carlo Engine
# Real Structured Note: Principal + Coupon + KO Down (Capital at Risk)
# Fair Value: Market price of the note (between 0 and 100)
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

np.random.seed(42)  # REPRODUCIBLE

class BasketType(Enum):
    WORST_OF = "worst_of"

class BarrierType(Enum):
    KO_DOWN = "ko_down"

@dataclass
class Barrier:
    type: BarrierType
    level: float  # Absolute price

class Structure:
    def __init__(self, name: str, underlyings: List[str], initial_prices: List[float],
                 barriers: List[Barrier], basket_type: BasketType,
                 maturity: float, principal: float = 100.0, coupon_rate: float = 0.0):
        self.name = name
        self.underlyings = underlyings
        self.initial_prices = np.array(initial_prices, dtype=np.float64)
        self.barriers = barriers
        self.basket_type = basket_type
        self.maturity = maturity
        self.principal = float(principal)
        self.coupon_rate = float(coupon_rate)

    @classmethod
    def from_json(cls, data: dict):
        underlyings = data.get("underlyings", ["Tencent", "Baba"])
        initial_prices = [float(p) for p in data.get("initial_prices", [100.0] * len(underlyings))]
        S0 = np.mean(initial_prices)
        maturity = float(data.get("maturity", 1.0))
        barriers = []
        for b in data.get("barriers", []):
            level = b["level"]
            if isinstance(level, str) and level.endswith("%"):
                level = float(level[:-1]) / 100 * S0
            barriers.append(Barrier(type=BarrierType[b["type"]], level=float(level)))
        principal = float(next((p["principal"] for p in data.get("other_props", []) if "principal" in p), 100.0))
        coupon = float(next((p["coupon"] for p in data.get("other_props", []) if "coupon" in p), 0.0))
        return cls(data.get("name", "Note"), underlyings, initial_prices, barriers, BasketType.WORST_OF, maturity, principal, coupon)

    def payoff(self, expiry_prices: np.ndarray) -> np.ndarray:
        worst_of_price = np.min(expiry_prices, axis=0)
        coupon_payment = (self.coupon_rate / 100) * self.maturity * self.principal

        gross_payoff = np.where(
            worst_of_price >= 98.0,
            self.principal + coupon_payment,  # Full capital + coupon
            worst_of_price                    # Capital at risk
        )
        return gross_payoff - self.principal  # Net to investor

def mc_value(structure: Structure, r: float = 0.05, sigma: float = 0.25, n_paths: int = 10000,
             n_steps: int = 1, correlations: np.ndarray = None) -> Dict[str, Any]:
    T = structure.maturity
    dt = T / max(n_steps, 1)
    n_assets = len(structure.underlyings)
    paths = np.zeros((n_assets, n_paths, n_steps + 1), dtype=np.float64)
    paths[:, :, 0] = structure.initial_prices[:, np.newaxis]
    correlations = correlations if correlations is not None else np.eye(n_assets)
    chol = np.linalg.cholesky(correlations)

    for t in range(1, n_steps + 1):
        z = np.dot(chol, np.random.standard_normal((n_assets, n_paths)))
        paths[:, :, t] = paths[:, :, t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

    expiry_prices = paths[:, :, -1]
    net_payoffs = structure.payoff(expiry_prices)
    fair_value_net = np.exp(-r * T) * np.mean(net_payoffs)
    fair_value_gross = structure.principal + fair_value_net
    prob_no_ko = np.mean(expiry_prices.min(axis=0) >= 98.0) * 100
    return {
        "fair_value_gross": float(fair_value_gross),
        "fair_value_net": float(fair_value_net),
        "prob_no_ko": float(prob_no_ko),
        "mean_net_payoff": float(np.mean(net_payoffs))
    }
