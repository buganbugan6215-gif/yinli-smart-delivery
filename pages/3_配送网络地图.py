import json

import folium
import streamlit as st
from streamlit_folium import st_folium

from 功能组件_页面共用代码.data_loader import load_site_data
from 功能组件_页面共用代码.ui import inject_css, page_title, render_sidebar, source_note

inject_css()
render_sidebar()
data = load_site_data()
page_title("配送地图", "一眼看清客户位置、配送范围和车辆路线")

if not data.customers.empty and {"纬度", "经度"}.issubset(data.customers.columns):
    center = [data.customers["纬度"].mean(), data.customers["经度"].mean()]
else:
    center = [30.85, 104.26]

product = st.selectbox("地图内容", ["全部路线", "鲜面条配送", "姜蒜专线"], index=0)
product_key = {"全部路线": "全部", "鲜面条配送": "N", "姜蒜专线": "G"}[product]

geo = data.geojson.get("routes", {})
customer_geo = data.geojson.get("customers", {})
if not geo or not geo.get("features"):
    st.info("暂无轻量路线 GeoJSON。网站仍可使用已整理的路线图片。")
    route_image = "展示图片_地图和答辩图/02_道路最短路径图/客户最短路径三联图.png"
    st.image(route_image, use_container_width=True)
else:
    fmap = folium.Map(location=center, zoom_start=11, tiles=None, control_scale=True)
    # 初版中文地图：使用高德中文道路底图，保留一个轻量简洁底图作为备用切换。
    folium.TileLayer(
        tiles="https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}",
        attr="© 高德地图",
        name="中文道路地图",
        subdomains="1234",
        overlay=False,
        control=True,
        show=True,
    ).add_to(fmap)
    folium.TileLayer(
        tiles="OpenStreetMap",
        attr="© OpenStreetMap contributors",
        name="开放街道底图",
        overlay=False,
        control=True,
        show=False,
    ).add_to(fmap)
    folium.Marker([30.85, 104.26], tooltip="配送中心", icon=folium.Icon(color="blue", icon="home")).add_to(fmap)
    for feature in geo.get("features", []):
        props = feature.get("properties", {})
        if product_key != "全部" and props.get("product_code") != product_key:
            continue
        coords = feature.get("geometry", {}).get("coordinates", [])
        if feature.get("geometry", {}).get("type") == "LineString" and coords:
            line = [[point[1], point[0]] for point in coords]
            color = "#1750df" if props.get("product_code") == "N" else "#ff8133"
            folium.PolyLine(line, color=color, weight=4, opacity=.85, tooltip=props.get("label", "配送路线")).add_to(fmap)
    for feature in customer_geo.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            continue
        if product_key != "全部" and props.get("product_code") != product_key:
            continue
        color = "#1750df" if props.get("product_code") == "N" else "#ff8133"
        popup = "<b>{}</b><br>配送品类：{}<br>订单量：{} kg<br>期望送达：{}".format(props.get("label", "客户"), props.get("product", "暂无"), props.get("demand_kg", "暂无"), props.get("time_window", "暂无"))
        folium.CircleMarker([coords[1], coords[0]], radius=5, color=color, fill=True, fill_opacity=.85, popup=popup, tooltip=props.get("label", "客户")).add_to(fmap)
    folium.LayerControl(collapsed=False, position="topright").add_to(fmap)
    st_folium(fmap, use_container_width=True, height=650, returned_objects=[])

st.caption("默认显示初版中文道路地图。路线来自已整理的道路路线数据；点击客户点可查看订单量和期望送达时间。")
source_note(data.manifest)
