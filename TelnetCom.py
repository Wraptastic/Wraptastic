import sys
import telnetlib
from ftplib import FTP
import time
import cv2
from matplotlib import pyplot as plt
import numpy as np
import os

# cognex's config
ip = "169.254.0.210"
user = 'admin'
password = ''

# telnet login
tn = telnetlib.Telnet(ip)
telnet_user = user+'\r\n'
tn.write(telnet_user.encode('ascii')) #the user name is admin
tn.write("\r\n".encode('ascii')) #there is no password - just return - now logged in
#print('Telnet Logged in')

# capture
tn.write(b"SE8\r\n")

# ftp login
ftp = FTP(ip)
ftp.login(user)
#print('FTP logged in')

# show all file in cognex
files_list = ftp.dir()
print(files_list)

# download file from cognex
filename = 'image.bmp'
lf = open(filename, "wb")
ftp.retrbinary("RETR " + filename, lf.write)
lf.close()

#read in image
cognex_img = cv2.imread('image.bmp')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#set image as base
base_img = cv2.imread('image.png')

#Convert color 
gray_base = cv2.cvtColor(base_img,cv2.COLOR_BGR2GRAY)
gray_img = cv2.cvtColor(cognex_img,cv2.COLOR_BGR2GRAY)

#Resize image from Cognex
width = int(gray_img.shape[1] * 0.8)
height = int(gray_img.shape[0] * 0.8)
dim1 = (width, height)
resized1 = cv2.resize(gray_img,dim1, interpolation = cv2.INTER_AREA)
cv2.imshow("Resized", resized1)
cv2.waitKey(1000)

#Blur image 
median_base = cv2.medianBlur(gray_base,3)
median_img = cv2.medianBlur(resized1, 3)

#Find threshold 
ret1, th1 = cv2.threshold(median_base, 0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
ret2, th2 = cv2.threshold(median_img, 0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

#Set kernel size and open image 
kernel = np.ones((3,3), np.uint8)
opening1 = cv2.morphologyEx(th1,cv2.MORPH_OPEN, kernel)
opening2 = cv2.morphologyEx(th2,cv2.MORPH_OPEN, kernel)

#Find contours 
cont1,_ = cv2.findContours(opening1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cont2,_ = cv2.findContours(opening2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

#Find biggest approx lenght 
for cnt in cont1:
    approx = cv2.approxPolyDP(cnt, .03 * cv2.arcLength(cnt, True), True)
    print(len(approx))
    if len(approx) == 8:
        cont_img1 = cv2.drawContours(gray_base, [cnt], -1, (255,255,0), 3)

for cnt in cont2:
    approx = cv2.approxPolyDP(cnt, .03 * cv2.arcLength(cnt, True), True)
    print(len(approx))
    if len(approx) == 8:
        cont_img2 = cv2.drawContours(resized1, [cnt], -1, (255,255,0), 3)

cv2.imshow("Contours1", cont_img1)
cv2.imshow("Contours2", cont_img2)
cv2.waitKey(0)

c1 = max(cont1,key = cv2.contourArea)
c2 = max(cont2,key = cv2.contourArea)
print(c1,c2)
x1,y1,w1,h1 = cv2.boundingRect(c1)
x2,y2,w2,h2 = cv2.boundingRect(c2)

#Locate contours with bounding rectangle 
cv2.rectangle(cont_img1, (x1,y1), (x1+w1,y1+h1), (255,255,0),5)
cv2.rectangle(cont_img2, (x2,y2), (x2+w2,y2+h2), (255,255,0),5)
cv2.imshow("Box1", cont_img1)
cv2.imshow("Box2", cont_img2)
cv2.waitKey(0)
cv2.destroyAllWindows()

#Cropp the image 
cropped_img1 = opening1[y1:y1+h1,x1:x1+w1]
cropped_img2 = opening2[y2:y2+h2,x2:x2+w2]

eroded1 = cv2.dilate(cropped_img1, (9,9), iterations=1)
eroded2 = cv2.dilate(cropped_img2, (9,9), iterations=1)
cv2.imshow("Eroded1", eroded1)
cv2.imshow("Eroded2", eroded2)
cv2.waitKey(0)



