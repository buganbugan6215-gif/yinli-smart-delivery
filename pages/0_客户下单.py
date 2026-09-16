import streamlit as st

from 功能组件_页面共用代码.order_state import create_order, init_orders
from 功能组件_页面共用代码.ui import inject_css, page_title, render_sidebar


inject_css()
render_sidebar()
init_orders()
page_title("客户下单", "填写配送需求，后续可随时查看处理进度")

st.markdown("""
<div class="service-hero motion-focus">
  <div><h2>把配送需求交给我们。</h2><p>地址、货量和时间填写完成后，订单会进入备货与车辆安排流程。</p></div>
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
    expected_time = t1.time_input("期望送达时间")
    latest_time = t2.time_input("最晚送达时间")
    note = st.text_area("配送备注", placeholder="例如：到店前请电话联系", height=88)
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
            "品类": product, "配送重量_kg": quantity, "期望送达": f"{delivery_date} {expected_time.strftime('%H:%M')}",
            "最晚送达": f"{delivery_date} {latest_time.strftime('%H:%M')}", "备注": note.strip(),
        })
        st.success(f"订单 {order['订单编号']} 已提交，当前状态：订单已提交。")
        st.session_state["active_order_id"] = order["订单编号"]
        st.page_link("pages/0_订单追踪.py", label="查看订单进度", use_container_width=True)

st.markdown("""
<div class="service-assurance motion-reveal">
  <div><b>信息清楚</b><span>订单、时间和状态统一记录</span></div>
  <div><b>进度可查</b><span>从提交到签收持续更新</span></div>
  <div><b>费用透明</b><span>生成方案后查看预计费用</span></div>
</div>
""", unsafe_allow_html=True)
