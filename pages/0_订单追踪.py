import streamlit as st

from 功能组件_页面共用代码.order_state import STATUS_FLOW, find_order, init_orders
from 功能组件_页面共用代码.ui import inject_css, page_title, render_sidebar


inject_css()
render_sidebar()
orders = init_orders()
page_title("订单追踪", "查看订单从提交、备货到配送签收的当前进度")

if not orders:
    st.markdown("<div class='empty-stage motion-focus'><h2>还没有可追踪的订单。</h2><p>先提交配送需求，订单进度会显示在这里。</p></div>", unsafe_allow_html=True)
    if st.button("创建配送订单", type="primary", use_container_width=True):
        st.switch_page("pages/0_客户下单.py")
    st.stop()

ids = [item["订单编号"] for item in orders]
default_id = st.session_state.get("active_order_id", ids[0])
selected = st.selectbox("选择订单", ids, index=ids.index(default_id) if default_id in ids else 0)
order = find_order(selected)
st.session_state["active_order_id"] = selected
index = int(order.get("状态序号", 0))

st.markdown(f"""
<div class="tracking-head motion-focus">
  <div><span>订单编号</span><h2>{order['订单编号']}</h2><p>{order['客户名称']} · {order['品类']} · {order['配送重量_kg']:,.0f} kg</p></div>
  <div class="tracking-state"><i></i><b>{order['状态']}</b><small>{order['数据模式']}</small></div>
</div>
<div class="delivery-track" style="--track:{index / (len(STATUS_FLOW)-1) * 100:.0f}%">
  <div class="delivery-track-fill"></div>
  {''.join(f'<div class="delivery-node {"done" if i <= index else ""}"><span>{i+1}</span><b>{label}</b></div>' for i, label in enumerate(STATUS_FLOW))}
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.2, .8], gap="large")
with left:
    st.markdown("### 配送信息")
    st.markdown(f"""
    <div class="detail-sheet motion-reveal">
      <div><span>收货地址</span><b>{order['收货地址']}</b></div>
      <div><span>期望送达</span><b>{order['期望送达']}</b></div>
      <div><span>最晚送达</span><b>{order['最晚送达']}</b></div>
      <div><span>预估费用</span><b>¥ {float(order.get('预估费用_元', 0)):,.2f}</b></div>
      <div><span>配送车辆</span><b>等待调度安排</b></div>
    </div>
    """, unsafe_allow_html=True)
with right:
    st.markdown("### 设备信息")
    st.info("车辆 GPS 与温度设备尚未接入。生成正式调度方案后，这里将显示车辆位置、预计到达和温控状态。")
    st.page_link("pages/3_配送网络地图.py", label="查看我的配送地图", use_container_width=True)
    if index == len(STATUS_FLOW) - 1 and st.button("完成电子签收", type="primary", use_container_width=True):
        st.switch_page("pages/8_电子签收.py")

st.markdown("<div class='demo-banner motion-reveal'><b>路线演示模式</b><span>当前仅展示订单流程；实时车辆位置与温度不会使用虚构数据。</span></div>", unsafe_allow_html=True)
