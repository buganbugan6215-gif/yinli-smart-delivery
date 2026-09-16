from pathlib import Path

import streamlit as st

from 功能组件_页面共用代码.data_loader import load_site_data
from 功能组件_页面共用代码.ui import inject_css, render_sidebar, source_note


ROOT = Path(__file__).resolve().parent
ROUTE_PREVIEW = ROOT / "展示图片_地图和答辩图" / "02_道路最短路径图" / "全部客户最短路径.png"

st.set_page_config(page_title="银犁智慧配送", page_icon="🚚", layout="wide", initial_sidebar_state="collapsed")
inject_css()
data = load_site_data()
render_sidebar()

st.markdown("""
<div class="home-nav">
  <div class="home-brand"><span>YL</span><strong>银犁智慧配送</strong></div>
  <div class="home-nav-copy">让每一次配送都有清楚的答案</div>
</div>
""", unsafe_allow_html=True)

with st.container(key="home_hero"):
    hero_copy, hero_visual = st.columns([1.03, 0.97], gap="large", vertical_alignment="center")
    with hero_copy:
        st.markdown("""
        <div class="home-hero-copy">
          <h1>从一份订单，到一套清楚的配送安排。</h1>
          <p>上传客户订单，快速看懂由谁配送、怎么走、何时到，以及预计花费。</p>
        </div>
        """, unsafe_allow_html=True)
        action_a, action_b = st.columns(2)
        with action_a:
            if st.button("上传订单", type="primary", use_container_width=True, key="hero_upload"):
                st.switch_page("pages/1_数据导入与方案生成.py")
        with action_b:
            if st.button("先看配送地图", use_container_width=True, key="hero_map"):
                st.switch_page("pages/3_配送网络地图.py")
        st.caption("支持 Excel、CSV 和已有配送结果，数据仅用于生成本次方案。")
    with hero_visual:
        if ROUTE_PREVIEW.exists():
            st.image(ROUTE_PREVIEW, caption="当前配送网络预览", use_container_width=True)
        else:
            st.info("路线预览正在准备中")

summary = data.summary.get("noodle", {})
if summary:
    st.markdown(f"""
    <div class="home-proof home-reveal">
      <div><strong>{summary.get('customers', '暂无')}</strong><span>个配送点</span></div>
      <div><strong>{summary.get('vehicles_used', '暂无')}</strong><span>辆车协同配送</span></div>
      <div><strong>{summary.get('total_distance_km', 0):,.1f}</strong><span>公里预计行程</span></div>
      <div><strong>¥ {summary.get('total_cost', 0):,.0f}</strong><span>预计配送费用</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<section class="home-section home-reveal">
  <h2>复杂的配送，留给平台处理。</h2>
  <p>您只需要提供订单，剩下的信息会被整理成容易确认、方便执行的页面。</p>
</section>
<div class="home-bento">
  <article class="home-feature home-feature-large home-reveal"><span class="feature-number">01</span><h3>看懂每一条路线</h3><p>客户位置、车辆路线和送达顺序集中在一张中文地图上，配送范围一目了然。</p><div class="feature-line"></div></article>
  <article class="home-feature home-feature-blue home-reveal"><span class="feature-number">02</span><h3>知道谁来配送</h3><p>每辆车负责哪些客户、装多少货、几点出发，都有明确安排。</p></article>
  <article class="home-feature home-feature-light home-reveal"><span class="feature-number">03</span><h3>提前了解费用</h3><p>把车辆、行驶和服务费用分开说明，减少沟通中的模糊地带。</p></article>
  <article class="home-feature home-feature-dark home-reveal"><span class="feature-number">04</span><h3>比较不同安排</h3><p>车辆数量、路线长短和预计费用并排展示，更容易选择合适方案。</p></article>
</div>
""", unsafe_allow_html=True)

with st.container(key="home_flow"):
    st.markdown("""
    <section class="home-section home-reveal"><h2>三步得到配送答案。</h2><p>从订单进入平台，到确认可执行方案，过程简单、结果清楚。</p></section>
    <div class="home-flow">
      <div class="home-flow-item home-reveal"><b>上传</b><span>放入客户、货量和时间要求</span></div>
      <div class="home-flow-item home-reveal"><b>安排</b><span>生成车辆、路线和送达顺序</span></div>
      <div class="home-flow-item home-reveal"><b>确认</b><span>查看地图、费用与服务结果</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<section class='home-section home-reveal'><h2>按您关心的内容直接进入。</h2></section>", unsafe_allow_html=True)
entry_cols = st.columns(4, gap="medium")
entries = [
    ("pages/0_客户下单.py", "客户下单", "提交配送需求", "订单"),
    ("pages/0_订单追踪.py", "订单追踪", "查看处理进度", "追踪"),
    ("pages/3_配送网络地图.py", "配送地图", "看位置与路线", "地图"),
    ("pages/7_企业工作台.py", "企业工作台", "处理订单与配送", "运营"),
]
for col, (page, title, copy, icon) in zip(entry_cols, entries):
    with col:
        with st.container(key=f"entry_{title}"):
            st.markdown(f"<div class='entry-icon'>{icon}</div>", unsafe_allow_html=True)
            st.page_link(page, label=title, use_container_width=True)
            st.caption(copy)

st.markdown("""
<div class="home-final home-reveal">
  <div><h2>准备好您的订单，配送安排从这里开始。</h2><p>上传后即可查看车辆、路线、预计到达和费用。</p></div>
</div>
""", unsafe_allow_html=True)
if st.button("开始生成配送方案", type="primary", use_container_width=True, key="final_upload"):
    st.switch_page("pages/1_数据导入与方案生成.py")

if data.errors:
    with st.expander("数据加载提示"):
        for error in data.errors:
            st.error(error)

source_note(data.manifest)
