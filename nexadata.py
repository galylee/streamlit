import pandas as pd
import requests

# 下秒数据 Nexadata
# http://demo.chafer.nexadata.cn
#
# 数据API操作


#目前开放的示例数据，可直接访问得到数据，不需要账号和token
#内置数据转换表
#其中的编码是来自数据视图的数据API的地址里面编码

POI_list={
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

#数据访问的header
#可在数据视图的数据API的设置里面找到
#当前的token是演示数据的token，需要更换为自己的token
#
def remote_header():
    headers = { "x-token": "tk09123cec03fe4450b33d6b33bcdb4734" }
    return headers

#生成Nexadata的远程数据访问地址
#可在数据视图的数据API的设置里面找到
def data_url(dataid,size=200,page=1):
    url=f"http://demo.chafer.nexadata.cn/openapi/v1/sheet/{dataid}/records?size={size}&page={page}"
    return url

#通过API，获得数据视图的数据
#dataid是数据视图编码，可以从数据视图的API设置里面得到
def load_table(dataid):

    #生成远程访问地址
    address=data_url(dataid)

    #请求的header，需要设置为自己的token
    header=remote_header()

    #访问远端服务，得到第一次的数据，获得数据大小以确定访问的页数
    response = requests.get(address, headers = header)
 
    data=response.json() #转换为JSON格式
    
    if data['code'] != 0:
        print(data)
        return 

    total=data['data']['total'] #数据的总条数
    size=data['data']['size']   #每次返回的条数
    pages=int(total/size)+2     #页数

    #存放结果的变量
    result_pandas=pd.DataFrame()

    #正式去掉所有页面的数据
    for i in range(1,pages):

        address=data_url(dataid,page=i)
        response = requests.get(address, headers = header)
        data=response.json()

        if data['code'] == 0:
            record=data['data']['list']
            record_frame = pd.DataFrame(record)
            #合并本次得到的数据到结果变量
            result_pandas=pd.concat([record_frame,result_pandas])

    return result_pandas


#通过名字获得某个视图的数据，名字的转换关系在POI_list字段里面
def load(data_name):

    #通过名字转换，获得视图的编码
    short_url=POI_list[data_name]

    #获得远程的数据视图
    result = load_table(short_url)

    return result

#转换经纬度字段的名字，转化为float类型
def transform_latlon(data):
    data = data.rename(columns={'经度': 'lon','纬度': 'lat'})
    data[['lat','lon']]=data[['lat','lon']].astype(float)
    return data
















