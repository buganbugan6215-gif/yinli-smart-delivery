from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


STATUS_FLOW = ["订单已提交", "仓库备货中", "等待装车", "配送途中", "配送完成"]


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
    orders.insert(0, order)
    return order


def find_order(order_id: str) -> dict[str, Any] | None:
    return next((item for item in init_orders() if item["订单编号"] == order_id), None)


def advance_order(order: dict[str, Any]) -> None:
    index = min(int(order.get("状态序号", 0)) + 1, len(STATUS_FLOW) - 1)
    order["状态序号"] = index
    order["状态"] = STATUS_FLOW[index]

