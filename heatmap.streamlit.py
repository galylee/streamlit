
import numpy as np
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

import numpy as np
import requests
import streamlit as st

nexadata_list={
    '星巴克':'sht21GiVwXqtc0',
    '麦当劳':'sht21CZvwmdLxQ',
    '肯德基':'sht21G1KJqKwQC',
    '瑞幸咖啡':'sht21Gn5NA1se0',
    '奈雪':'sht21GlesqSdPs',
    '书亦烧仙草':'sht21GlBX4wXC4',
    '购物中心':'sht21GnozwiD0i',
    '全家':'sht21HXDum5CTo',
    '屈臣氏':'sht21HZhqhGr0y',
    '美宜佳':'sht21Ha7PSuRjE',
    '良品铺子':'sht21IAv4poX0S',
    '喜茶':'sht21GlNBIR13Q',
    '太平洋咖啡':'sht21IBqPgzakq',
    'COSTA咖啡':'sht21IC7dBF13g',
}

colors=['red', 'blue', 'green', 'purple', 'orange', 'darkred',
'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']


tile_geoq='http://map.geoq.cn/ArcGIS/rest/services/ChinaOnlineStreetGray/MapServer/tile/{z}/{y}/{x}'

m=folium.Map([23.11868, 113.3225],
           tiles=tile_geoq,
           attr='高德-中英文对照',
           zoom_start=13,
          )

fg = folium.FeatureGroup(name="State bounds")


def get_nexadata_header():
    headers = { "x-token": "tk09123cec03fe4450b33d6b33bcdb4734" }
    return headers

def get_nexadata_url(dataid,size=200,page=1):
    url=f"http://demo.chafer.nexadata.cn/openapi/v1/sheet/{dataid}/records?size={size}&page={page}"
    return url

def get_nexadata_table(dataid):
    address=get_nexadata_url(dataid)
    header=get_nexadata_header()
    response = requests.get(address, headers = header)
 
    data=response.json()
        
    if data['code'] != 0:
        print(data)
        return 

    result_pandas=pd.DataFrame()
    total=data['data']['total']
    size=data['data']['size']
    pages=int(total/size)+2


    for i in range(1,pages):
        address=get_nexadata_url(dataid,page=pages)
        response = requests.get(address, headers = header)
        if data['code'] == 0:
            record=data['data']['list']
            record_frame = pd.DataFrame(record)
            result_pandas=pd.concat([record_frame,result_pandas])

#    df = dframe.rename(columns={'经度': 'Longitude','纬度': 'Latitude'})
    return result_pandas

#    df2=df[['Latitude','Longitude']].astype(float)

def nexadata_latlon(data):
    data = data.rename(columns={'经度': 'lon','纬度': 'lat'})
    data[['lat','lon']]=data[['lat','lon']].astype(float)
    return data

def nexadata_load(data_name):
    print(data_name)
    short_url=nexadata_list[data_name]
    result = get_nexadata_table(short_url)
    result = nexadata_latlon(result)
    return result


def nexadata_add_layer(m,name, data,color):
    group = folium.FeatureGroup(name=name, control=True)

    for index, row in data.iterrows():
        group.add_child(folium.Circle(radius=10,color=color,location=[row["lat"], row["lon"]]))

    m.add_child(group)

    return 

def nexadata_add_marker(m,fg, data,color):

    for index, row in data.iterrows():
        fg.add_child(folium.Circle(radius=10,color=color,location=[row["lat"], row["lon"]]))

    return 






options=''

def maker_to_map(fg):
    i=0
    for o in options:
        datas = nexadata_load(o)
        color = colors[i]
        nexadata_add_marker(m,fg,datas,color)
        st.write(o,color)
        i=i+1
    return

def heatmap_to_map(fg):
    i=0
    for o in options:
        datas = nexadata_load(o)
        datas=nexadata_latlon(datas)
        datas=datas[['lat','lon']]
        fg.add_child(HeatMap(datas, name=o))
        i=i+1
    return

keys_list = list(nexadata_list.keys())
st.header('Nexadata POI热力图分布')

# Using object notation

options = st.multiselect(
    '请选择POI类别名称',
    keys_list)

heatmap_to_map(fg)

st_data = st_folium(m, feature_group_to_add=fg,width=1600)















