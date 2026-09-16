import streamlit as st

from 功能组件_页面共用代码.order_state import find_order, init_orders
from 功能组件_页面共用代码.ui import inject_css, page_title, render_sidebar


inject_css()
render_sidebar()
orders = init_orders()
page_title("电子签收", "记录收货结果并生成当前会话的电子回单")

if not orders:
    st.info("当前没有可签收的订单。")
    if st.button("返回客户下单", type="primary", use_container_width=True):
        st.switch_page("pages/0_客户下单.py")
    st.stop()

ids = [item["订单编号"] for item in orders]
selected = st.selectbox("选择订单", ids)
order = find_order(selected)

st.markdown(f"<div class='receipt-head motion-focus'><span>{order['订单编号']}</span><h2>{order['客户名称']}</h2><p>{order['品类']} · {order['配送重量_kg']:,.0f} kg · {order['收货地址']}</p></div>", unsafe_allow_html=True)

with st.form("receipt_form"):
    c1, c2 = st.columns(2)
    receiver = c1.text_input("收货人姓名")
    actual = c2.number_input("实际收货重量（kg）", min_value=0.0, value=float(order["配送重量_kg"]), step=1.0)
    result = st.radio("收货情况", ["正常签收", "部分签收", "拒收"], horizontal=True)
    problems = st.multiselect("异常情况", ["包装破损", "数量不符", "温度异常", "送达延迟", "其他"])
    note = st.text_area("签收说明", placeholder="没有异常可不填写")
    photo = st.file_uploader("签收照片（可选）", type=["jpg", "jpeg", "png"])
    agreed = st.checkbox("确认以上收货信息真实无误")
    done = st.form_submit_button("确认签收并生成回单", type="primary", use_container_width=True)

if done:
    if not receiver.strip() or not agreed:
        st.error("请填写收货人姓名并确认收货信息。")
    else:
        order["状态"] = "配送完成"
        order["状态序号"] = 4
        order["签收结果"] = result
        order["收货人"] = receiver.strip()
        receipt = f"银犁智慧配送电子回单\n订单编号：{selected}\n客户：{order['客户名称']}\n品类：{order['品类']}\n计划重量：{order['配送重量_kg']} kg\n实收重量：{actual} kg\n签收结果：{result}\n异常情况：{'、'.join(problems) if problems else '无'}\n签收说明：{note or '无'}\n收货人：{receiver.strip()}\n数据说明：本回单生成于当前网站会话。"
        st.success("签收完成，订单状态已更新。")
        st.download_button("下载电子回单", receipt.encode("utf-8-sig"), f"{selected}_电子回单.txt", "text/plain", use_container_width=True)
