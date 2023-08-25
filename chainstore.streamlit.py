
import streamlit as st
import pandas 
import numpy as np
import requests

headers = { "x-token": "tk09123cec03fe4450b33d6b33bcdb4734" }

for i in range(1,2):

    url=f"http://demo.chafer.nexadata.cn/openapi/v1/sheet/sht21CZvwmdLxQ/records"

    
    response = requests.get(url, headers = headers)
    data=response.json()
    print(data)
    record=data['data']['list']
    dframe=pandas.DataFrame(record)
    df = dframe.rename(columns={'经度': 'lon','纬度': 'lat'})
    print(df)

df2=df[['lat','lon']].astype(float)


st.map(df2)
st.dataframe(data=df)