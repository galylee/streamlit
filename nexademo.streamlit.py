import streamlit as st
import nexadata as nd
import geocoding

st.title(' 下秒数据 nexadata POI可视化')

option = st.selectbox(
     '请选择品牌',
     (nd.POI_list))

#st.write('You selected:', option)

startbucks=nd.load(option)

startbucks=ng.transform_latlon(startbucks)

for i,row in startbucks.iterrows():
    lon,lat = geocoding.gcj02_to_wgs84(row['lon'], row['lat'])
    startbucks.at[i,'lon']=lon
    startbucks.at[i,'lat']=lat

st.map(startbucks)
st.dataframe(startbucks)
