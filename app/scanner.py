import re
from typing import Optional, Dict

def parse_deal(text: str) -> Optional[Dict]:
    text = text.lower()
    months = re.search(r"(\d+)\s*months?", text)
    ko = re.search(r"ko\s*(\d+)%", text)
    coupon = re.search(r"(\d+(?:\.\d+)?)%\s*coupon", text)
    assets = re.findall(r"\b(tencent|baba|hsbc|hang seng|apple|google)\b", text)[:2]
    if not months or len(assets) < 1:
        return None
    return {
        "name": f"{'_'.join([a.title() for a in assets])}_KO{ko.group(1) if ko else '100'}",
        "basket": [a.title() for a in assets],
        "maturity_months": int(months.group(1)),
        "ko": int(ko.group(1)) if ko else 100,
        "coupon": float(coupon.group(1)) if coupon else 0.0,
        "principal": 100.0
    }
