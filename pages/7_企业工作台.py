import pandas as pd
import streamlit as st

from 功能组件_页面共用代码.data_loader import load_site_data
from 功能组件_页面共用代码.order_state import advance_order, init_orders
from 功能组件_页面共用代码.ui import fmt_money, inject_css, page_title, render_sidebar


inject_css()
render_sidebar()
data = load_site_data()
orders = init_orders()
page_title("企业工作台", "把订单、车辆、路线和待接入设备放在同一个运营视图中")

summary = data.summary.get("noodle", {})
st.markdown("""
<div class="ops-ribbon motion-focus"><span>今日运营</span><b>从订单进入，到配送完成</b><div class="pulse-route"><i></i></div></div>
""", unsafe_allow_html=True)

metrics = st.columns(4)
metrics[0].metric("当前会话订单", len(orders))
metrics[1].metric("参考可用车辆", summary.get("vehicles_used", "暂无"))
metrics[2].metric("参考配送里程", f"{summary.get('total_distance_km', 0):,.1f} km")
metrics[3].metric("参考方案费用", fmt_money(summary.get("total_cost")))

st.markdown("### 订单流转")
if not orders:
    st.markdown("<div class='empty-stage motion-reveal'><h3>当前没有客户提交的订单</h3><p>客户下单后，订单会自动进入这里。</p></div>", unsafe_allow_html=True)
else:
    labels = [f"{item['订单编号']} · {item['客户名称']} · {item['状态']}" for item in orders]
    chosen_label = st.selectbox("选择需要处理的订单", labels)
    chosen = orders[labels.index(chosen_label)]
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<div class='ops-order motion-reveal'><span>{chosen['品类']}</span><h3>{chosen['客户名称']}</h3><p>{chosen['配送重量_kg']:,.0f} kg · {chosen['期望送达']}</p><b>{chosen['状态']}</b></div>", unsafe_allow_html=True)
        if st.button("推进到下一状态", type="primary", use_container_width=True, disabled=chosen["状态"] == "配送完成"):
            advance_order(chosen)
            st.rerun()
    with c2:
        frame = pd.DataFrame(orders)
        show = [c for c in ["订单编号", "客户名称", "品类", "配送重量_kg", "期望送达", "状态"] if c in frame.columns]
        st.dataframe(frame[show], use_container_width=True, hide_index=True)

st.markdown("### 系统接入状态")
st.markdown("""
<div class="integration-rail">
  <div class="ready motion-reveal"><span>订单与调度</span><b>已接入</b><small>现有订单、车辆、路线和费用数据</small></div>
  <div class="waiting motion-reveal"><span>仓储库存</span><b>等待数据</b><small>库存、分拣、月台和装车记录</small></div>
  <div class="waiting motion-reveal"><span>车辆设备</span><b>等待设备</b><small>GPS 位置与车厢温度记录</small></div>
  <div class="waiting motion-reveal"><span>历史预测</span><b>等待积累</b><small>历史订单达到可用规模后启用</small></div>
</div>
""", unsafe_allow_html=True)
