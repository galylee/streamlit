import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import sqlite3
from folium.plugins import HeatMap


def display_heatmap(df, longitude_field, latitude_field):
    # 创建地图并设置初始中心坐标
    m = folium.Map(location=[23.1251, 113.3229])
    # 添加GEOQ的灰色地图瓦片图层
    tile_layer = folium.TileLayer(
        tiles="http://map.geoq.cn/ArcGIS/rest/services/ChinaOnlineStreetGray/MapServer/tile/{z}/{y}/{x}",
        attr="GEOQ",
        name="GEOQ灰色底图",
    )
    tile_layer.add_to(m)
    # 添加热力图
    locations = df[[latitude_field, longitude_field]].values
    HeatMap(locations).add_to(m)

    # 显示地图
    st_data = st_folium(m, width=1600)


def save_uploaded_file(uploaded_file):
    with open(os.path.join("uploads", uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def load_csv_files():
    files = os.listdir("uploads")
    csv_files = [file for file in files if file.endswith(".csv")]
    return csv_files


def save_to_database(df, table_name):
    conn = sqlite3.connect("data.db")
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()


def load_from_database(table_name):
    conn = sqlite3.connect("data.db")
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def display_data(df):
    st.write(df)


def display_map(df, longitude_field, latitude_field, color):
    # 创建地图并设置初始中心坐标
    m = folium.Map(location=[23.1251, 113.3229])

    # 添加GEOQ的灰色地图瓦片图层
    tile_layer = folium.TileLayer(
        tiles="http://map.geoq.cn/ArcGIS/rest/services/ChinaOnlineStreetGray/MapServer/tile/{z}/{y}/{x}",
        attr="GEOQ",
        name="GEOQ灰色底图",
    )
    tile_layer.add_to(m)

    # 在地图上添加标记
    for index, row in df.iterrows():
        longitude = row[longitude_field]
        latitude = row[latitude_field]
        popup_text = f"经度: {longitude}<br>纬度: {latitude}"
        folium.Circle(
            location=[latitude, longitude],
            radius=5,
            popup=popup_text,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
        ).add_to(m)

    # 显示地图
    st_data = st_folium(m, width=1600)


def main():
    st.title("CSV 文件可视化")

    # 创建用于保存上传文件的文件夹
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # 上传CSV文件
    uploaded_file = st.sidebar.file_uploader("上传CSV文件", type="csv")
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)

    # 显示已上传的CSV文件列表
    csv_files = load_csv_files()
    selected_file = st.sidebar.selectbox("选择要显示的CSV文件", csv_files)

    if selected_file:
        st.subheader(selected_file)
        df = pd.read_csv(os.path.join("uploads", selected_file))
        display_data(df)

        # 获取CSV文件字段列表
        fields = df.columns.tolist()

        # 检查字段列表是否包含经度和纬度
        if "经度" in fields and "纬度" in fields:
            longitude_field = "经度"
            latitude_field = "纬度"
        else:
            # 选择经度字段
            longitude_field = st.sidebar.selectbox("选择经度字段", fields)

            # 选择纬度字段
            latitude_field = st.sidebar.selectbox("选择纬度字段", fields)

        # 选择颜色
        color = st.sidebar.color_picker("选择标记颜色")

        # 保存数据到数据库
        table_name = selected_file.split(".")[0]  # 使用文件名作为表名
        save_to_database(df, table_name)

        # 从数据库加载数据
        df_from_db = load_from_database(table_name)

        display_map(df_from_db, longitude_field, latitude_field, color)

        display_heatmap(df_from_db, longitude_field, latitude_field)


if __name__ == "__main__":
    main()
