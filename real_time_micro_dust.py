import googlemaps
from bs4 import BeautifulSoup
import pandas as pd
import time 
import re 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import folium
import json

gmaps_key = "__GOOGLE_KEY_"
gmaps = googlemaps.Client(key=gmaps_key)

#Translation into Korean
def loc_to_kor_nm(lat, lon):
    addr= gmaps.reverse_geocode((lat,lon), language="ko")
    kor_nm = addr[0].get("formatted_address")
    return kor_nm[5:]

#Crawling
targetUrl = 'https://aqicn.org/map/southkorea'
html = urlopen(targetUrl).read()
soup = BeautifulSoup(html, 'html.parser')
links = soup.find('div', id='map-stations').find_all('a')
 
df = pd.DataFrame(columns=('kor_nm', 'pm25', 'pm10', 'lat', 'lon'))

i = 0
for link in links:
    targetUrl = link.get('href')
    html = urlopen(targetUrl).read()
    soup = BeautifulSoup(html, 'html.parser')
    #Get city information
    info = str(soup.select_one('#citydivouter > script'))
    match = re.search(r'"city":(.*?)"}' ,info)
    json_string = '{' + match.group(0) +'}'
    info_list = json.loads(json_string)
    pm25 = soup.find('td', id='cur_pm25').string
    pm10 = soup.find('td', id='cur_pm10').string
    geo = list(map(float, info_list['city']['geo']))
    lat, lon = geo[0], geo[1]
    kor_nm = loc_to_kor_nm(lat, lon)
    df.loc[i] = [ kor_nm, pm25, pm10, lat, lon]
    i = i + 1
    time.sleep(0.5) 
 
#Data cleansing
df[['pm25', 'pm10']] = df[['pm25', 'pm10']].apply(pd.to_numeric, errors = 'coerce') #to number
df = df.dropna() #Clear rows without values
df[['pm25', 'pm10']] = df[['pm25', 'pm10']].astype(int)

#Categorization
bins = [0, 50, 100, 150, 200, 300, 500]
labels_num = [0, 1, 2, 3, 4, 5] 
labels_string = ['좋음', '보통', '민감군영향', '나쁨', '매우나쁨', '위험']
df['pm10_grade_N'] = pd.cut(df['pm10'], bins,  include_lowest= False, right=True, labels=labels_num)
df['pm10_grade'] = pd.cut(df['pm10'], bins, include_lowest= False, right=True,  labels=labels_string)
df['pm25_grade_N'] = pd.cut(df['pm25'], bins,  include_lowest= False, right=True, labels=labels_num)
df['pm25_grade'] = pd.cut(df['pm25'], bins, include_lowest= False, right=True,  labels=labels_string)

colordict = {0:'green', 1:'yellow', 2:'orange', 3:'red', 4:'purple', 5:'black'}

#pm10 
m = folium.Map(location=[36.49, 127.20], zoom_start=7)

for i, lat, lon, pm10, city, grade_N, grade in zip(range(len(df)), df['lat'], df['lon'], df['pm10'], df['kor_nm'], df['pm10_grade_N'], df['pm10_grade']):
    folium.CircleMarker(
        [lat, lon], 
        tooltip = str(city) + '<br>' + '미세먼지: ' + str(pm10) + '<br>' + grade,  
        popup = str(city) + '<br>' + '미세먼지: ' + str(pm10) + '<br>' + grade, 
        radius = int(pm10)*0.2, 
        color ='b ',
        threshold_scale = [0, 1, 2, 3, 4, 5],
        fill_color = colordict[grade_N],
        fill = True,
        fill_opacity = 0.7
    ).add_to(m)

m.save('pm10.html')

#pm25 

m2 = folium.Map(location=[36.49, 127.20], zoom_start=7)

for i, lat, lon, pm25, city, grade_N, grade in zip(range(len(df)), df['lat'], df['lon'], df['pm25'], df['kor_nm'], df['pm25_grade_N'], df['pm25_grade']):
    folium.CircleMarker(
        [lat, lon], 
        tooltip = str(city) + '<br>' + '초미세먼지: ' + str(pm25) + '<br>' + grade,  
        popup = str(city) + '<br>' + '초미세먼지: ' + str(pm25) + '<br>' + grade, 
        radius = int(pm25)*0.1, 
        color ='b ',
        threshold_scale = [0, 1, 2, 3, 4, 5],
        fill_color = colordict[grade_N],
        fill = True,
        fill_opacity = 0.7
    ).add_to(m2)

m2.save('pm25.html')


df.to_csv('data.csv', encoding='ANSI')
