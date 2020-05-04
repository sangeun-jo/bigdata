import PIL.ImageGrab
import webbrowser
import time
import win32com.client
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import imageio
from PIL import Image
import matplotlib.image as mpimg
from datetime import datetime

shell = win32com.client.Dispatch("WScript.Shell")

#Get yesterday's date
year = str(datetime.today().year)
month = str(datetime.today().month).zfill(2)      
yesterday = str(datetime.today().day-1).zfill(2)    

st = year + '/' + month+'/'
st1 = year+month+yesterday

os.makedirs(st1) 
pathIn= st1+'/' #Automatically create folders by date in which pictures will be stored
pathOut = './gif/' + st1 +'.gif' #The location where gif will be stored. Must be made in advance

t1 = "https://earth.nullschool.net/#"  #Real-time fine dust path site. Just show it on the website
t2 = "Z/particulates/surface/level/overlay=pm2.5/orthographic=125.47,36.09,2507/loc=127.199,37.494" #pm25, Korean coordinates
count=0

#Capture and save pm25 path yesterday every hour
for tz in range(0,24,1): 
    tt = t1+st+yesterday+"/"+str(tz).zfill(2)+"00"+t2    
    d1=st1+str(count).zfill(4) 
    webbrowser.open(tt,new=0)
    time.sleep(5)
    img = PIL.ImageGrab.grab()
    cutted_img = img.crop((0,150,1904,1014))
    cutted_img.save(pathIn +str(str(d1)+'.png'),'png') 
    shell.SendKeys("^w") 
    count+=1

#Create gif
path = [pathIn+f"{i}" for i in os.listdir(pathIn)] 
im = [ Image.open(i) for i in path]  
imageio.mimsave(pathOut, im, fps=3) #3 fps per 1 second 