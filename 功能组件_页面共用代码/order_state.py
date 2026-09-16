from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


STATUS_FLOW = ["订单已提交", "仓库备货中", "等待装车", "配送途中", "配送完成"]
ROOT = Path(__file__).resolve().parents[1]
ORDER_DATA_DIR = ROOT / "客户订单数据"
REFERENCE_UNIT_COST = {"鲜面条": 3076.952624401527 / 2655.0, "姜蒜": 3598.9971890530455 / 8831.0}


def estimate_delivery_fee(product: str, quantity_kg: float) -> float:
    """按当前已核验方案的平均单位配送成本给出客户参考价。"""
    return round(max(0.0, float(quantity_kg)) * REFERENCE_UNIT_COST.get(product, 0.0), 2)


def save_order_to_excel(order: dict[str, Any]) -> str:
    """按送达日期和品类保存订单；云端文件在应用重启后可能被清理。"""
    delivery_date = str(order.get("期望送达日期") or datetime.now().date())
    product = str(order.get("品类", "未分类"))
    folder = ORDER_DATA_DIR / delivery_date
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{product}订单.xlsx"
    row = pd.DataFrame([{key: value for key, value in order.items() if key not in {"状态序号"}}])
    if path.exists():
        existing = pd.read_excel(path)
        row = pd.concat([existing, row], ignore_index=True)
    row.to_excel(path, index=False)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def init_orders() -> list[dict[str, Any]]:
    if "customer_orders" not in st.session_state:
        st.session_state["customer_orders"] = []
    return st.session_state["customer_orders"]


def create_order(payload: dict[str, Any]) -> dict[str, Any]:
    orders = init_orders()
    now = datetime.now()
    order = {
        "订单编号": f"YL{now:%m%d%H%M%S}",
        "提交时间": now.strftime("%Y-%m-%d %H:%M"),
        "状态": STATUS_FLOW[0],
        "状态序号": 0,
        "数据模式": "当前会话订单",
        **payload,
    }
    order.setdefault("预估费用_元", estimate_delivery_fee(str(order.get("品类", "")), float(order.get("配送重量_kg", 0))))
    try:
        order["保存路径"] = save_order_to_excel(order)
        order["保存状态"] = "已写入订单表"
    except Exception as exc:
        order["保存状态"] = f"写入失败：{exc}"
    orders.insert(0, order)
    return order


def find_order(order_id: str) -> dict[str, Any] | None:
    return next((item for item in init_orders() if item["订单编号"] == order_id), None)


def advance_order(order: dict[str, Any]) -> None:
    index = min(int(order.get("状态序号", 0)) + 1, len(STATUS_FLOW) - 1)
    order["状态序号"] = index
    order["状态"] = STATUS_FLOW[index]
