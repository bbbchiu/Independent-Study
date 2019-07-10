import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
import subprocess
from pylepton import Lepton
import select
import picamera.array

HOST = '192.168.68.196'
PORT = 6667

def capture(flip_v = False, device = "/dev/spidev0.0"):
    with Lepton(device) as l:
        a,_ = l.capture()
        b = np.copy(a)
    if flip_v:
        cv2.flip(a,0,a)
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)
    return np.uint8(a), np.uint16(b)
    #return np.uint16(a)

def img_capture():
    global tmp1,flir_val,s,flir_img
    t0 = time.time()
    flir_img,flir_val = capture()
    #flir_val = capture()
    #print(flir_val)
    
    t1 = time.time()
    tmp1 = np.empty((480,640,3),dtype = np.uint8)
    camera.capture(tmp1,'bgr',use_video_port = True)
    '''
    camera.capture("ir2.jpg",use_video_port = True)
    tmp1 = cv2.imread('ir2.jpg')
    flir_img = cv2.applyColorMap(flir_img,cv2.COLORMAP_JET)
    cv2.imwrite("flir2.jpg",flir_img)
    t2 = time.time()
    '''
    #print("flir_time = ",t1-t0)
    #print("ir_time = ",t2-t1)
    try:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
    except:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST,PORT))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
            s.send(("Nadine").ljust(16).encode())
        except:
            pass


#def img_processing(ir_img,flir_val):
def img_processing():
    global img_combine,tmp1,flir_img,dst
    flir_img = cv2.applyColorMap(flir_img,cv2.COLORMAP_JET)
    flir_img = cv2.resize(flir_img,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
    dst = cv2.warpPerspective(flir_img,matrix,(ir_weight,ir_height))
    img_combine = cv2.addWeighted(tmp1,0.5,dst,0.5,0)

count = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
packet_size = 10000
request_flag = 0
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
move_y = 24
move_x = 50
th_70 = 7680        #8900
th_100 = 7700       #9650
refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
tmp1 = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
matrix = np.loadtxt('matrix.txt',delimiter = ',')
try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())
    save_msg_count = 0

    #pic_count = 0
    while True:
    #while(pic_count<100):
        #pic_count+=1
        '''
        t0 = time.time()
        flir_img, flir_val = capture()
        t1 = time.time()

        camera.capture(stream,format= 'bgr' ,use_video_port = True)
        tmp1 = stream.array
        stream.truncate(0)
        #camera.capture("ir1.jpg",use_video_port = True)
        #tmp1 = cv2.imread('ir1.jpg')

        t2 = time.time()
        print("flir_time = ",t1-t0)
        print("ir_time = ",t2-t1)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
        '''
        #thread_img = threading.Thread(target = img_capture)
        #thread_img.start()
        img_capture()
        img_processing()
        #img_processing(tmp1,flir_val)
        cv2.imshow("combine",img_combine)
        cv2.waitKey(1)
        '''
        print("before thread")
        thread_img = threading.Thread(target = img_processing,args=(tmp1,flir_val,))
        thread_img.start()
        print("after thread")
        if(refresh):
            refresh = False
            cv2.imshow("combine",img_combine)
            cv2.waitKey(1)
        '''
        #cv2.imshow('flir',flir_img)
        #cv2.imshow('picamera',tmp)
        #cv2.waitKey(1)
        
        
finally:
        camera.close()
        s.close()






