import streamlit as st

from 功能组件_页面共用代码.order_state import create_order, estimate_delivery_fee, init_orders
from 功能组件_页面共用代码.ui import inject_css, page_title, render_sidebar


inject_css()
render_sidebar()
init_orders()
page_title("客户下单", "填写收货信息和送达时间，提交前即可查看预估费用")

st.markdown("""
<div class="service-hero motion-focus">
  <div><h2>把配送需求交给我们。</h2><p>信息填写完成后，系统会保存订单并进入备货与车辆安排流程。</p></div>
  <div class="service-orbit"><span></span><b>订单正在进入配送网络</b></div>
</div>
""", unsafe_allow_html=True)

with st.form("customer_order_form", clear_on_submit=False):
    st.markdown("### 收货信息")
    c1, c2 = st.columns(2)
    customer = c1.text_input("客户名称", placeholder="例如：青羊区某门店")
    contact = c2.text_input("联系人", placeholder="收货联系人")
    c3, c4 = st.columns([1.4, 1])
    address = c3.text_input("收货地址", placeholder="请填写详细地址")
    phone = c4.text_input("联系电话", placeholder="用于配送联系")

    st.markdown("### 配送内容")
    p1, p2, p3 = st.columns(3)
    product = p1.selectbox("配送品类", ["鲜面条", "姜蒜"])
    quantity = p2.number_input("配送重量（kg）", min_value=1.0, value=100.0, step=10.0)
    delivery_date = p3.date_input("期望送达日期")
    t1, t2 = st.columns(2)
    expected_time = t1.time_input("最早到达时间")
    latest_time = t2.time_input("最晚送达时间")
    st.caption("预计送达时间误差不超过半小时；配送高峰时段可能更长，届时请留意来电。")
    estimated_fee = estimate_delivery_fee(product, quantity)
    st.markdown(f"""
    <div class="fee-preview">
      <span>本单预估配送费用</span><strong>¥ {estimated_fee:,.2f}</strong>
      <small>按当前已核验方案的平均单位配送成本估算，最终费用以调度路线核算为准。</small>
    </div>
    """, unsafe_allow_html=True)
    submitted = st.form_submit_button("提交配送订单", type="primary", use_container_width=True)

if submitted:
    missing = [name for name, value in [("客户名称", customer), ("收货地址", address), ("联系人", contact), ("联系电话", phone)] if not value.strip()]
    if missing:
        st.error("请补充：" + "、".join(missing))
    elif latest_time <= expected_time:
        st.error("最晚送达时间需要晚于期望送达时间。")
    else:
        order = create_order({
            "客户名称": customer.strip(), "联系人": contact.strip(), "联系电话": phone.strip(), "收货地址": address.strip(),
            "品类": product, "配送重量_kg": quantity, "期望送达日期": str(delivery_date),
            "最早到达": expected_time.strftime('%H:%M'), "最晚到达": latest_time.strftime('%H:%M'),
            "期望送达": f"{delivery_date} {expected_time.strftime('%H:%M')}",
            "最晚送达": f"{delivery_date} {latest_time.strftime('%H:%M')}", "预估费用_元": estimated_fee,
        })
        st.success(f"订单 {order['订单编号']} 已提交，预估费用 ¥ {order['预估费用_元']:,.2f}。")
        st.session_state["active_order_id"] = order["订单编号"]
        if order.get("保存状态") == "已写入订单表":
            st.caption(f"订单已按日期和品类保存：{order.get('保存路径')}")
        else:
            st.warning("订单已进入当前会话，但写入 Excel 失败。工作人员可从当前订单列表导出。")
        st.page_link("pages/0_订单追踪.py", label="查看订单进度", use_container_width=True)
