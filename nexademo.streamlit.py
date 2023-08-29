import streamlit as st
import nexadata as nd
import geocoding

# Initialization
if 'option' not in st.session_state:
    st.session_state['option'] = '星巴克'


def selected():
    option=st.session_state['option']
    #st.write(option)

    startbucks=nd.load(option)

    startbucks=nd.transform_latlon(startbucks)

    for i,row in startbucks.iterrows():
        lon,lat = geocoding.gcj02_to_wgs84(row['lon'], row['lat'])
        startbucks.at[i,'lon']=lon
        startbucks.at[i,'lat']=lat

    st.map(startbucks)
    st.dataframe(startbucks)

st.title(' 下秒数据 nexadata POI可视化')

option = st.selectbox(
     '请选择品牌',
     (nd.POI_list))
st.session_state['option']=option

selected()



