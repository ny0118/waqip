# coding: utf-8

"""
    To download air quality from World Air Quality Index Project and calculate each elements value based on iaqi for each
    elements using multi processors
"""

#-------Yang Nan----2020-03-19

import numpy as np
import pandas as pd
import pymysql #需要1  20-03-19
from sqlalchemy import create_engine #需要2 20-03-19


#from .aqi import aqi
from waqip import WAQIP

def get_waqip(token, cities=None, latlng=None):
    '''
    :param token (str):
    :param cities (list):
    :param latlng (list):
    :return:
    '''
    columns = ['date', 'tz', 'city', 'idx', 'lat', 'lon',
               'aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3', 'co',
               'h', 't', 'r', 'w']
    dfs = pd.DataFrame(columns=columns)

    waqip = WAQIP(token)

    if cities is not None:
        for city in cities:
            df = waqip.get_city(city)
            print('city : {0}\nurl : {1}\n'.format(waqip.city, waqip.url))
            dfs = dfs.append(df, ignore_index=True)
    elif latlng is not None:
        for lat, lon in latlng:
            df = waqip.get_latlon(lat, lon)
            dfs = dfs.append(df, ignore_index=True)
    else:
        raise ValueError('Please ensure cities or latlng must be is not None at least!')

    return dfs

def main(cities):
    dfs = get_waqip('f903f45f3a6dbca9f1bc790ea60c24aa65e50e59', cities=cities) # replace your_token to your token from WAQIP

    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/waqip')  # your mysql port and database name
    print(dfs)

    dfs['city'] = dfs.city.str.encode('utf-8')
    dfs.to_sql(name='aqi_test_nanyang', con=engine, if_exists='append', index=False)


if __name__=='__main__':

    import multiprocessing
    from sqlalchemy import create_engine

    #stds = pd.read_csv('cities_china_url.csv', index_col=0)
    stds = pd.read_csv('cities_china_url_2.csv', index_col=0) #读取CSV文件
    #print(stds)
    cities = stds.idx.values #获取idx项数值
    #print(cities)

    pool = multiprocessing.Pool(processes=12) # set the number of processors

    for i in np.arange(0, len(cities), 20):
        pool.apply_async(main, [cities[i:i+20]])
        print('loop ', i)

    pool.close()
    pool.join()
