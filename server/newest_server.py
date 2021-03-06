from windows import Ui_Form
from client_struct import client
import selectors
import socket
import numpy as np
import os
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer, Qt
import cv2
import time
import types

class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initVar() 

        ##### Set Timer
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(100)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.get_socket_data)
        self.timer2.start(10)

        self.timer3 = QTimer(self)
        self.timer3.timeout.connect(self.check_time)
        self.timer3.start(1000)

        self.timer4 = QTimer(self)
        self.timer4.timeout.connect(self.set_image_info)
        self.timer4.start(100)

        ##### Set Button
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.btn_info.clicked.connect(self.on_click_btn_info)
        self.ui.btn_map.clicked.connect(self.on_click_btn_map)
        self.ui.btn_image.clicked.connect(self.on_click_btn_image)
        self.ui.btn_choose.clicked.connect(self.on_click_btn_choose)
        self.ui.btn_ok.clicked.connect(self.on_click_btn_ok)
        self.ui.btn_remove.clicked.connect(self.on_click_btn_remove)
        self.ui.btn_reset.clicked.connect(self.on_click_btn_reset)
        self.ui.btn_back.clicked.connect(self.on_click_btn_back)
        self.ui.btn_choose.setEnabled(True)
        self.ui.btn_remove.setEnabled(True)
        self.ui.btn_ok.setEnabled(True)
        self.ui.btn_choose.setVisible(True)
        self.ui.btn_remove.setVisible(True)
        self.ui.btn_ok.setVisible(True)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_reset.setVisible(False)
        self.ui.btn_back.setEnabled(False)
        self.ui.btn_back.setVisible(False)
        
        ##### Set Label
        self.ui.label.setScaledContents(True)
        self.offset_x = self.ui.label.geometry().width()
        self.offset_y = self.ui.label.geometry().height()

        #### Initialized
        self.img_map_loading()
        self.socket_initialize()
        self.showMaximized()
        self.show()

    def initVar(self): ##### Initialize Global Variable
        self.count = 0
        ##### Images
        self.image_image = np.zeros((800,800,3),np.uint8)
        self.image_map = np.zeros((800,800,3),np.uint8)
        self.image_info = np.zeros((800,800,3),np.uint8)
        self.keep = np.zeros((800,800,3),np.uint8)
        self.no_wifi_image = np.zeros((800,800,3),np.uint8)
        self.img_fireman = [ ]
        self.keep_fire = []     
        self.img_queue_size = 300  
 
        ##### Offsets of mouse clicking
        self.offset_x = 1
        self.offset_y = 1

        ##### Flags
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False   
        self.ok_flag = False
        self.choose_flag = False 
        self.remove_flag = False 
        self.back_flag = False
        self.info_flag = 0
        self.refresh_map = False                                      
        self.refresh_img = False
        self.click_to_cancel = False
        self.inti_flag = -1
        
        ##### Socket Connect
        self.disconnect_number = 0
        self.connect_number = 0
        self.host = '192.168.68.196'
        self.port = 8888
        self.client_list = [client(0,self.img_queue_size),client(1,self.img_queue_size),client(2,self.img_queue_size),client(3,self.img_queue_size)]
        self.connection_num = np.zeros(4)
        self.subplot_count = [0, 1, 2, 3]
        self.client_dict = {"client":1}
        
        self.time_press = 0
        
        ##### Length
        self.name_space_height = 50 
        self.resize_height = 480+200
        self.resize_weight = 640+600
        self.height = 480
        self.weight = 640
        self.map_width = 1174
        self.map_height = 705
        self.max_x = self.map_width*2                                 
        self.max_y = self.map_height*2
        self.middle_x = 1170    ##### middle of map image
        self.middle_y = 700

        self.click_client = 0    ##### the client you click in window
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        self.hot_mask = []
        self.explosion_mask = []
        self.init_time = 0
        self.time_to_come_out = 2880
        self.start_point = (0,0)    ##### for draw rectangle
        self.end_point = (0,0)
        self.release_mouse = False
        self.count_back_img = self.img_queue_size
        self.choose_fireman = -1 
    
    def on_click_btn_info(self):
        self.image_image_flag = False
        self.image_map_flag = False
        self.image_info_flag = True
        self.back_flag = False
        self.count_back_img = self.img_queue_size
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(False)
        self.ui.btn_remove.setEnabled(False)
        self.ui.btn_choose.setVisible(False)
        self.ui.btn_ok.setVisible(False)
        self.ui.btn_remove.setVisible(False)
        self.ui.btn_reset.setEnabled(True)
        self.ui.btn_reset.setVisible(True)
        self.ui.btn_back.setEnabled(False)
        self.ui.btn_back.setVisible(False)

    def on_click_btn_map(self):
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False
        self.back_flag = False
        self.count_back_img = self.img_queue_size
        self.ui.btn_choose.setEnabled(True)
        self.ui.btn_ok.setEnabled(True)
        self.ui.btn_remove.setEnabled(True)
        self.ui.btn_choose.setVisible(True)
        self.ui.btn_ok.setVisible(True)    
        self.ui.btn_remove.setVisible(True)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_reset.setVisible(False)
        self.ui.btn_back.setEnabled(False)
        self.ui.btn_back.setVisible(False)

    def on_click_btn_image(self):
        self.image_image_flag = True
        self.image_map_flag = False
        self.image_info_flag = False
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(False)     
        self.ui.btn_remove.setEnabled(False)
        self.ui.btn_choose.setVisible(False)
        self.ui.btn_ok.setVisible(False)    
        self.ui.btn_remove.setVisible(False)
        self.ui.btn_reset.setEnabled(False)
        self.ui.btn_reset.setVisible(False)
        self.ui.btn_back.setEnabled(True)
        self.ui.btn_back.setVisible(True)

    def on_click_btn_back(self):
        self.image_image_flag = True
        self.image_map_flag = False
        self.image_info_flag = False
        self.choose_flag = False
        self.remove_flag = False
        self.ok_flag = False
        if(self.disconnect_number > 0):
            self.back_flag = True
            self.ui.btn_back.setEnabled(False)

    def on_click_btn_choose(self):
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False
        self.choose_flag = True
        self.remove_flag = False
        self.ui.btn_info.setEnabled(False)
        self.ui.btn_map.setEnabled(False)
        self.ui.btn_image.setEnabled(False)
        self.ui.btn_remove.setEnabled(False)
        self.ui.btn_ok.setEnabled(True)    
        
    def on_click_btn_remove(self):
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False
        self.choose_flag = False
        self.remove_flag = True
        self.ui.btn_info.setEnabled(False)
        self.ui.btn_map.setEnabled(False)
        self.ui.btn_image.setEnabled(False)
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(True)  

    def on_click_btn_ok(self):
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False
        self.ok_flag = True
        self.ui.btn_info.setEnabled(True)
        self.ui.btn_map.setEnabled(True)
        self.ui.btn_image.setEnabled(True)
        self.ui.btn_choose.setEnabled(True)
        self.ui.btn_remove.setEnabled(True)
        if not (self.choose_fireman == -1):
            if(self.choose_flag):
                self.replace_roi(self.explosion_mask, self.choose_fireman, self.start_point[1], self.end_point[1], self.start_point[0], self.end_point[0], (1,1,1))
                self.choose_flag = False
            elif(self.remove_flag):
                self.replace_roi(self.explosion_mask, self.choose_fireman, self.start_point[1], self.end_point[1], self.start_point[0], self.end_point[0], (0,0,0))
                self.remove_flag = False
            self.draw_layer(self.choose_fireman)
            self.choose_fireman = -1
            self.start_point = (0,0)
            self.end_point = (0,0)

    def on_click_btn_reset(self):
        if(self.info_flag == 1):
            self.client_list[self.info_flag].time_in = time.time() - self.time_to_come_out + 5
        else:
            self.client_list[self.info_flag].time_in = time.time()

    def update_image(self):
        if(self.image_image_flag):
            if((self.connect_number == 0 ) and (self.disconnect_number >0)):
                ###### no one connect ######
                if(self.back_flag):
                    self.count_back_img -= 1
                ###### concatenate and plot image ######
                img_concate_Hori=np.concatenate((self.client_list[0].read_img(self.back_flag),self.client_list[1].read_img(self.back_flag)),axis=1)
                img_concate_Verti=np.concatenate((self.client_list[2].read_img(self.back_flag),self.client_list[3].read_img(self.back_flag)),axis=1)
                img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                self.image_image = cv2.resize(img_toshow,(self.resize_weight,self.resize_height),interpolation=cv2.INTER_CUBIC)
                if(self.count_back_img == 0):
                    self.count_back_img = self.img_queue_size
                    self.back_flag = False
                    self.ui.btn_back.setEnabled(True)
            image = self.image_image.copy()
        elif(self.image_map_flag):
            image = self.image_map.copy()
            if(self.choose_flag or self.remove_flag):
                if(self.release_mouse):
                    cv2.rectangle(image, self.start_point, self.end_point, (0, 255, 0), 2)
        elif(self.image_info_flag):
            image = self.image_info.copy()
        else:
            image = self.image_map.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        QIm = QImage(image.data, image.shape[1], image.shape[0],image.shape[1] *image.shape[2],QImage.Format_RGB888)
        self.ui.label.setPixmap(QPixmap.fromImage(QIm))

    def mousePressEvent(self,event):
        if(event.button() == Qt.LeftButton):
            if(self.choose_flag or self.remove_flag):
                press_x = int(event.pos().x()*self.offset_x)
                press_y = int(event.pos().y()*self.offset_y)
                self.start_point = (press_x, press_y)
                self.release_mouse = False
                if(press_x < self.middle_x and press_y < self.middle_y):
                    self.choose_fireman = 0
                elif(press_x >= self.middle_x and press_y < self.middle_y):
                    self.choose_fireman = 1
                elif(press_x < self.middle_x and press_y >= self.middle_y):
                    self.choose_fireman = 2
                elif(press_x >= self.middle_x and press_y >= self.middle_y):
                    self.choose_fireman = 3
                else:
                    pass

    def mouseReleaseEvent(self,event):
        press_x = int(event.pos().x()*self.offset_x)
        press_y = int(event.pos().y()*self.offset_y)
        fireman = -1
        if(event.button() == Qt.LeftButton):
            if(self.image_map_flag):
                if(press_x < self.middle_x and press_y < self.middle_y):
                    fireman = 0
                elif(press_x >= self.middle_x and press_y < self.middle_y):
                    fireman = 1
                elif(press_x < self.middle_x and press_y >= self.middle_y):
                    fireman = 2
                elif(press_x >= self.middle_x and press_y >= self.middle_y):
                    fireman = 3
                else:
                    pass

                if(self.choose_flag or self.remove_flag):
                    ###### choose the explosion area ######
                    if(self.choose_fireman == -1):
                        return 
                    else:
                        end_x = 0
                        end_y = 0
                        ###### avoid choose area out of bounds ######
                        if(press_x > self.client_list[self.choose_fireman].explosion_bound_right):
                            end_x = self.client_list[self.choose_fireman].explosion_bound_right
                        elif(press_x < self.client_list[self.choose_fireman].explosion_bound_left):
                            end_x = self.client_list[self.choose_fireman].explosion_bound_left
                        else:
                            end_x = press_x
                        if(press_y > self.client_list[self.choose_fireman].explosion_bound_bottom):
                            end_y = self.client_list[self.choose_fireman].explosion_bound_bottom
                        elif(press_y < self.client_list[self.choose_fireman].explosion_bound_top):
                            end_y = self.client_list[self.choose_fireman].explosion_bound_top
                        else:
                            end_y = press_y
                        self.end_point = (end_x, end_y)
                    self.release_mouse = True
                    self.draw_layer(0)   
                else:
                    if(self.connection_num[fireman] == 1 and self.client_list[fireman].set_start == False):
                        self.client_list[fireman].position_x = press_x
                        self.client_list[fireman].position_y = press_y
                        self.client_list[fireman].set_start = True
                        self.draw_layer(0)
                        self.refresh_map = True
                    elif(self.connection_num[fireman] == 1 and self.client_list[fireman].direction == -1):
                        if(abs(press_x - self.client_list[fireman].position_x) > abs(press_y- self.client_list[fireman].position_y)):
                            if(press_x > self.client_list[fireman].position_x):
                                self.client_list[fireman].direction = 90
                            else:
                                self.client_list[fireman].direction = 270
                        else:
                            if(press_y > self.client_list[fireman].position_y):
                                self.client_list[fireman].direction = 180
                            else:
                                self.client_list[fireman].direction = 0
                    else:
                        pass
            elif(self.image_image_flag):
                self.click_to_cancel = True
                if(press_x < self.middle_x and press_y < self.middle_y):
                    self.click_client = 0
                elif(press_x >= self.middle_x and press_y < self.middle_y):
                    self.click_client = 1
                elif(press_x < self.middle_x and press_y >= self.middle_y):
                    self.click_client = 2
                elif(press_x >= self.middle_x and press_y >= self.middle_y):
                    self.click_client = 3
                else:
                    self.click_to_cancel = False   
            else:
                pass
        else:
            pass

    def keyPressEvent(self,event):
        if(event.key() == Qt.Key_1 and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = 0
        elif(event.key() == Qt.Key_2 and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = 1
        elif(event.key() == Qt.Key_3 and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = 2
        elif(event.key() == Qt.Key_4 and time.time() - self.time_press > 1): 
            self.time_press = time.time()
            self.info_flag = 3
        else:  
            if(event.key() == Qt.Key_Up):
                for i in self.client_list:
                    i.position_y-=100
                self.draw_layer(0)
            elif(event.key() == Qt.Key_Down):
                for i in self.client_list:
                    i.position_y+=100
                self.draw_layer(0)
            elif(event.key() == Qt.Key_Left):
                for i in self.client_list:
                    i.position_x-=100
                self.draw_layer(0)
            elif(event.key() == Qt.Key_Right):
                for i in self.client_list:
                    i.position_x+=100
                self.draw_layer(0)

    def img_map_loading(self):
        fireman_img_map_path = "../IMAGE/fireman.png"
        map_img_map_path = "../IMAGE/1f.png"
        wifi_img_path = "../IMAGE/wifi_images.png"                                
         
        if(os.path.isfile(wifi_img_path)):
            self.no_wifi_image = cv2.imread(wifi_img_path,-1)
        if(os.path.isfile(fireman_img_map_path)):
            print("Reading FireFighter Image...")
            while(len(self.img_fireman) == 0):
                self.img_fireman = cv2.imread(fireman_img_map_path,-1)
            self.img_fireman = cv2.resize(self.img_fireman,(50,50))
        else:
            print("There is no FireFighter Image")

        self.image_map = [] 
        print("Reading Environment Map...")
        if(os.path.isfile(map_img_map_path)):
            while(len(self.image_map) == 0):
                self.image_map = cv2.imread(map_img_map_path)
        print("Merge Map For Four FireFighters...")
        self.image_map = np.hstack((self.image_map,self.image_map))
        self.image_map = np.vstack((self.image_map,self.image_map))
 
        print("Drawing Security Line...")
        index = 0
        while index < 4:
            line_left_spot_x = self.client_list[index].line_left_spot_x
            line_right_spot_x = self.client_list[index].line_right_spot_x
            line_up_spot_y = self.client_list[index].line_up_spot_y
            line_down_spot_y = self.client_list[index].line_down_spot_y
            left_thickness = self.client_list[index].left_thickness
            right_thickness = self.client_list[index].right_thickness
            up_thickness = self.client_list[index].up_thickness
            down_thickness = self.client_list[index].down_thickness
            cv2.line(self.image_map,(line_left_spot_x,line_up_spot_y),(line_right_spot_x,line_up_spot_y),self.client_list[index].color_set,up_thickness,6)
            cv2.line(self.image_map,(line_left_spot_x,line_down_spot_y),(line_right_spot_x,line_down_spot_y),self.client_list[index].color_set,down_thickness,6)
            cv2.line(self.image_map,(line_left_spot_x,line_up_spot_y),(line_left_spot_x,line_down_spot_y),self.client_list[index].color_set,left_thickness,6)
            cv2.line(self.image_map,(line_right_spot_x,line_up_spot_y),(line_right_spot_x,line_down_spot_y),self.client_list[index].color_set,right_thickness,6)
            index += 1
 
        print("Set Initialize Map")
        self.keep = self.image_map.copy()
        self.hot_mask = np .zeros(self.image_map.shape,np.uint8)
        self.explosion_mask = np .zeros(self.image_map.shape,np.uint8)
        self.draw_layer(0)
        self.keep_fire = self.image_map.copy()
        self.offset_x = self.image_map.shape[1] / self.offset_x
        self.offset_y = self.image_map.shape[0] / self.offset_y

    def socket_initialize(self):    
        self.sel = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host,self.port))
        lsock.listen()
        print('listening on', (self.host, self.port))
        #lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        print("Waiting For Connection...")


    def get_socket_data(self):
        events = self.sel.select(timeout=0.01)
        for key, mask in events:
            if key.data is None:
                self.accept_wrapper(key.fileobj)
            else:
                self.service_connection(key, mask)
                
                if(self.refresh_img or self.refresh_map or self.info_flag >= 0):
                    if(self.refresh_img):
                        self.refresh_img = False
                        ###### concatenate and plot image ######
                        if(self.back_flag):
                            self.count_back_img -= 1
                        img_concate_Hori=np.concatenate((self.client_list[0].read_img(self.back_flag),self.client_list[1].read_img(self.back_flag)),axis=1)
                        img_concate_Verti=np.concatenate((self.client_list[2].read_img(self.back_flag),self.client_list[3].read_img(self.back_flag)),axis=1)
                        img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                        self.image_image = cv2.resize(img_toshow,(self.resize_weight,self.resize_height),interpolation=cv2.INTER_CUBIC)
                        if(self.count_back_img == 0):
                            self.count_back_img = self.img_queue_size
                            self.back_flag = False
                            self.ui.btn_back.setEnabled(True)
                    if(self.click_to_cancel):
                        self.set_namespace_color(self.click_client,(255,255,255),(0, 0, 0))
                        if(self.client_list[self.click_client].sos_flag):
                            self.client_list[self.click_client].send_save_msg_flag = True
                        self.client_list[self.click_client].set_sos_flag(False)
                        self.click_to_cancel = False
 
    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)    
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        ###### create an client object an put into dictionary with it's address ######
        min_num = min(self.subplot_count)
        ###### create an white image with client name ######
        self.client_list[min_num]=client(min_num,self.img_queue_size)
        self.client_list[min_num].set_visible(True)
        self.client_dict[str(addr[1])] = min_num
        ###### number remove from list subplot_count ######
        self.subplot_count.remove(min_num)
        self.connect_number += 1
        #--------------------------------------------------------------#
        i = 0                                                             
        while(i<4):
            if(self.connection_num[i] == 0):
                self.client_list[i].set_info(i,addr)
                self.connection_num[i] = 1
                inti_flag = i
                self.client_list[i].time_in = time.time()
                self.client_list[i].disconnect_flag = False
                break
            i = i + 1
            # add new connection
            # 創造一個新的Object給Device
        #--------------------------------------------------------------------#
    
        print("Client: ")
        print("\tnum: ",self.client_list[i].id_num)
        print("\tip_addr: ",self.client_list[i].ip_addr)
    
 
    def set_namespace_color(self,client_index,background_color,font_color):
        namespace_whiteimg = np.zeros((self.name_space_height,self.weight,3), np.uint8)
        namespace_whiteimg[:,:] = background_color
        name = self.client_list[client_index].get_name()
        cv2.putText(namespace_whiteimg, name, (200, 42), cv2.FONT_HERSHEY_SIMPLEX, 2, font_color, 3, cv2.LINE_AA)
        self.client_list[client_index].set_namespace(namespace_whiteimg)
 
    def service_connection(self,key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = None
            client_host = self.client_dict[str(data.addr[1])]
            if(self.client_list[client_host].first_time_recv()):
                print("Getting Name...")
                recv_data = sock.recv(16)
                name = recv_data.decode()
                self.client_list[client_host].set_name(name)
                ###### Default : white background black font ######
                self.set_namespace_color(client_host,(255,255,255),(0, 0, 0))   
                print("The Name is: ",name)
                self.init_time = time.time() 
            else:
                if(self.client_list[client_host].get_package_size() <= 0):
                    try:
                        ###### recv the image size ######
                        recv_data = sock.recv(16)
                        recv_data_msg = recv_data.decode().strip()
                        if("FLIR" in recv_data_msg):
                            self.client_list[client_host].set_package(int(recv_data_msg[4:len(recv_data_msg)]),2)
                        elif("IR" in recv_data_msg):
                            self.client_list[client_host].set_package(int(recv_data_msg[2:len(recv_data_msg)]),1)
                        elif("TH70" in recv_data_msg):
                            self.client_list[client_host].set_threshold(1, float(recv_data_msg[4:len(recv_data_msg)]))
                        elif("TH100" in recv_data_msg):
                            self.client_list[client_host].set_threshold(2, float(recv_data_msg[5:len(recv_data_msg)]))
                        elif(len(recv_data_msg) == 0):
                            pass
                        else:
                            try:
                                #------------------------------------------------------------------#
                                for i in self.client_list:
                                    if(i.ip_addr == data.addr):
                                        i.time_pass = time.time() - self.init_time
                                        if("HELP2" in recv_data_msg):
                                            self.client_list[client_host].set_sos_flag(True)
                                            self.client_list[client_host].yellow_flag = False
                                            self.draw_layer(client_host)
                                        elif("HELP" in recv_data_msg):
                                            self.client_list[client_host].yellow_flag = True
                                            self.draw_layer(client_host)
                                        elif("NUM" in recv_data_msg):
                                            i.fire_num = recv_data_msg[3:len(recv_data_msg)]
                                        elif("DRAW" in recv_data_msg):
                                            self.drawNewSpot(recv_data_msg[4:len(recv_data_msg)],i.id_num)     
                                            if(self.client_list[client_host].sos_flag):    
                                                self.set_namespace_color(client_host,(255,255,255),(0, 0, 0))
                                                self.client_list[client_host].set_sos_flag(False)
                                            self.client_list[client_host].yellow_flag = False
                                            self.client_list[client_host].send_save_msg_flag = False
                                        else:
                                            break
                                    # Device 傳輸資料時, call 對應function
                                #--------------------------------------------------------------------#
                            except Exception as e:
                                print ("error in other msg: ",e.args)
                    except Exception as e:
                        print ("error in get msg: ",e.args)
                        #pass
                    
                else:
                    ###### recv the img ######
                    try:
                        recv_data = sock.recv(self.client_list[client_host].get_package_size())
                        ###### concatenate recv msg to image ######
                        self.client_list[client_host].combine_recv_img(recv_data)
                        self.client_list[client_host].decrease_package_size(len(recv_data))
                        if(self.client_list[client_host].get_package_size() <= 0):
                            ###### image recv complete ######
                            send_flag = self.client_list[client_host].decode_img()
                            if(send_flag):
                                self.refresh_img = True
                                send_flag = False
                                try:
                                    combine = self.client_list[client_host].read_combine_img()
                                    _,encode = cv2.imencode('.jpg', combine, self.encode_param)
                                    data_combine = np.array(encode)
                                    stringData = data_combine.tostring()
                                    sock.send(str(len(stringData)).ljust(16).encode())
                                    sock.send(stringData)
                                except Exception as e:
                                    self.count += 1
                                    print("error in send image to client : ",e.args,self.count)
                                ###### decide which background color to brush ######
                                brush_background_ornot = self.client_list[client_host].brush_namespace_background()
                                if(brush_background_ornot == 1):
                                    ###### Red background with white font ######
                                    self.set_namespace_color(client_host,(0,0,255),(255, 255, 255))
                                elif (brush_background_ornot == 2):
                                    ###### White background with black font ######
                                    self.set_namespace_color(client_host,(255,255,255),(0, 0, 0))
                            self.client_list[client_host].set_package(-1,0)
                    except Exception as e:
                        print ("error in get image msg: ",e.args)
                        self.client_list[client_host].except_for_img()
 
            if not recv_data:
                print('closing connection to', data.addr)
                #-------------------------------------------------------------------#
                print(str(data.addr[0]))
                print(self.client_list[0].ip_addr)
                for i in self.client_list:
                    if(i.ip_addr == data.addr):
                        self.connection_num[i.id_num] = 1
                        i.disconnect_real_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                        i.disconnect_time = time.time() - i.time_in
                        i.disconnect_flag = True
                        self.add_no_wifi(i.id_num)
                self.drawNewSpot('0.0',0)
                self.refresh_map = True
                # Close Connection 的時候取消 Object
                #--------------------------------------------------------------------#
                self.connect_number -= 1
                self.disconnect_number += 1
                self.refresh_img = True
                self.client_list[self.client_dict[str(data.addr[1])]].set_back_img_num()
                self.client_list[self.client_dict[str(data.addr[1])]].disconnect_flag = True
                self.sel.unregister(sock)
                sock.close()

    def drawNewSpot(self,data,index):
        if("No Turn" in data):
            self.client_list[index].addNewPosition("No Turn",0)
        elif("Left" in data):
            self.client_list[index].addNewPosition("Left",0)
        elif("Right" in data):
            self.client_list[index].addNewPosition("Right",0)
        else:
            self.client_list[index].addNewPosition("No Turn",float(data))
        self.refresh_map = True
        self.draw_layer(index)     
        
    def helpConditionExec(self,message,index):
        if("HELP2" in message):
            self.client_list[index].color_set = (0,0,255)
        elif("HELP" in message):
            self.client_list[index].color_set = (0,165,255)
        else:
            pass

        line_left_spot_x = self.client_list[index].line_left_spot_x
        line_right_spot_x = self.client_list[index].line_right_spot_x
        line_up_spot_y = self.client_list[index].line_up_spot_y
        line_down_spot_y = self.client_list[index].line_down_spot_y
        left_thickness = self.client_list[index].left_thickness
        right_thickness = self.client_list[index].right_thickness
        up_thickness = self.client_list[index].up_thickness
        down_thickness = self.client_list[index].down_thickness
        cv2.line(self.image_map,(line_left_spot_x,line_up_spot_y),(line_right_spot_x,line_up_spot_y),self.client_list[index].color_set,up_thickness,6)
        cv2.line(self.image_map,(line_left_spot_x,line_down_spot_y),(line_right_spot_x,line_down_spot_y),self.client_list[index].color_set,down_thickness,6)
        cv2.line(self.image_map,(line_left_spot_x,line_up_spot_y),(line_left_spot_x,line_down_spot_y),self.client_list[index].color_set,left_thickness,6)
        cv2.line(self.image_map,(line_right_spot_x,line_up_spot_y),(line_right_spot_x,line_down_spot_y),self.client_list[index].color_set,right_thickness,6)
        
    def replace_roi(self, dst, num, y0, y1, x0, x1, roi):
        if(y0 > y1):
            y0, y1 = y1, y0
        if(x0 > x1):
            x0, x1 = x1, x0
        dst[y0 : y1 , x0 : x1] = roi
        if(num==0):
            next_y0 = y0 + self.map_height
            next_y1 = y1 + self.map_height
            next_x0 = x0 + self.map_width
            next_x1 = x1 + self.map_width
            dst[y0 : y1 , next_x0 : next_x1] = roi
            dst[next_y0 : next_y1 , x0 : x1] = roi
            dst[next_y0 : next_y1 , next_x0 : next_x1] = roi
        elif(num==1):
            last_x0 = x0 - self.map_width
            last_x1 = x1 - self.map_width
            next_y0 = y0 + self.map_height
            next_y1 = y1 + self.map_height
            dst[y0 : y1 , last_x0 : last_x1] = roi
            dst[next_y0 : next_y1 , x0 : x1] = roi
            dst[next_y0 : next_y1 , last_x0 : last_x1] = roi
        elif(num==2):
            next_x0 = x0 + self.map_width
            next_x1 = x1 + self.map_width
            last_y0 = y0 - self.map_height
            last_y1 = y1 - self.map_height
            dst[y0 : y1 , next_x0 : next_x1] = roi
            dst[last_y0 : last_y1 , x0 : x1] = roi
            dst[last_y0 : last_y1 , next_x0 : next_x1] = roi
        else:
            last_y0 = y0 - self.map_height
            last_y1 = y1 - self.map_height
            last_x0 = x0 - self.map_width
            last_x1 = x1 - self.map_width
            dst[y0 : y1 , last_x0 : last_x1] = roi
            dst[last_y0 : last_y1 , x0 : x1] = roi
            dst[last_y0 : last_y1 , last_x0 : last_x1] = roi

    def draw_layer(self,num):
        self.image_map = self.keep.copy()
        for draw_client in self.client_list:
            if(draw_client.sos_flag):
                self.helpConditionExec("HELP2",draw_client.id_num)
            elif(draw_client.yellow_flag):
                self.helpConditionExec("HELP",draw_client.id_num)
        alpha_s = self.img_fireman[:,:,3] / 255.0
        alpha_l = 1.0 - alpha_s
        ###### avoid img_fireman out of bounds ######
        if(self.client_list[num].position_x > self.client_list[num].fireman_bound_right):
            x_offset = self.client_list[num].fireman_bound_right - 50
        elif(self.client_list[num].position_x < self.client_list[num].fireman_bound_left):
            x_offset = self.client_list[num].fireman_bound_left
        else:
            x_offset = self.client_list[num].position_x-25
        if(self.client_list[num].position_y > self.client_list[num].fireman_bound_bottom):
            y_offset = self.client_list[num].fireman_bound_bottom - 50
        elif(self.client_list[num].position_y < self.client_list[num].fireman_bound_top):
            y_offset = self.client_list[num].fireman_bound_top
        else:
            y_offset = self.client_list[num].position_y-25

        ###### refresh hot mask ######
        if(self.client_list[num].in_danger_flag):
            self.replace_roi(self.hot_mask, num, y_offset, self.img_fireman.shape[0] + y_offset, x_offset, self.img_fireman.shape[1] + x_offset, (1,1,1))
            self.client_list[num].in_danger_flag = False
        else:
            self.replace_roi(self.hot_mask, num, y_offset, self.img_fireman.shape[0] + y_offset, x_offset, self.img_fireman.shape[1] + x_offset, (0,0,0))
        
        index_tuple = np.where(self.hot_mask[:,:,0]==1)
        row = index_tuple[0]
        col = index_tuple[1]
        for c in range(0,2):     
            self.image_map[row,col,c] = self.image_map[row, col, c]*0.5
        self.image_map[row, col, 2] = self.image_map[row, col, 0]*0.5 + 122
        ###### refresh explosion mask ######
        index_tuple = np.where(self.explosion_mask[:,:,0]==1)
        row = index_tuple[0]
        col = index_tuple[1]
        self.image_map[row, col, 2] = self.image_map[row, col, 2]*0.5
        self.image_map[row, col, 1] = self.image_map[row, col, 1]*0.5
        self.image_map[row, col, 0] = self.image_map[row, col, 0]*0.5 + 122
        for fireman in self.client_list:
            ###### avoid img_fireman out of bounds ######
            if(fireman.position_x > fireman.fireman_bound_right):
                x_offset = fireman.fireman_bound_right - 50
            elif(fireman.position_x < fireman.fireman_bound_left):
                x_offset = fireman.fireman_bound_left
            else:
                x_offset = fireman.position_x - 25
            if(fireman.position_y > fireman.fireman_bound_bottom):
                y_offset = fireman.fireman_bound_bottom - 50
            elif(fireman.position_y < fireman.fireman_bound_top):
                y_offset = fireman.fireman_bound_top
            else:
                y_offset = fireman.position_y - 25
            
            x2 = self.img_fireman.shape[1] + x_offset
            y2 = self.img_fireman.shape[0] + y_offset
            for c in range(3):
                self.image_map[y_offset:y2 , x_offset:x2, c] = (alpha_s * self.img_fireman[:,:,c] + alpha_l * self.image_map[y_offset:y2 , x_offset:x2, c])
            ###### detect_danger ######
            x1 = fireman.position_x-50
            y1 = fireman.position_y-50
            x2 = fireman.position_x+50
            y2 = fireman.position_y+50
            left_spot_x = fireman.left_spot_x
            right_spot_x = fireman.right_spot_x
            up_spot_y = fireman.up_spot_y
            down_spot_y = fireman.down_spot_y

            if x1 < left_spot_x:
                x1 = left_spot_x
            elif x1 > right_spot_x:
                x1 = right_spot_x
            else:
                pass
            if x2 < left_spot_x: 
                x2 = left_spot_x 
            elif x2 > right_spot_x:
                x2 = right_spot_x
            else:   
                pass

            if y1 < up_spot_y:
                y1 = up_spot_y
            elif y1 > down_spot_y:
                y1 = down_spot_y
            else:
                pass

            if y2 < up_spot_y:  
                y2 = up_spot_y  
            elif y2 > down_spot_y:
                y2 = down_spot_y
            else:   
                pass    
            y3 = y1+35
            y4 = y2-35
            x3 = x1+35
            x4 = x2-35
            if(y3 > y4):
                y3,y4 = y4,y3
            if(x3 > x4):
                x3,x4 = x4,x3
            if (np.sum(self.explosion_mask[y3:y4, x3:x4]) > 0):
                fireman.in_explosion_flag = True
                fireman.closing_danger_flag = False
            elif ((np.sum(self.hot_mask[y1:y2, x1:x2]) > 0) or (np.sum(self.explosion_mask[y1:y2, x1:x2]) > 0)):
                fireman.in_explosion_flag =False
                fireman.in_danger_flag = False
                fireman.closing_danger_flag = True
            else:
                fireman.in_explosion_flag =False
                fireman.in_danger_flag = False
                fireman.closing_danger_flag = False

    def set_image_info(self):
        # reset image_info
        self.image_info = self.image_map.copy()
        left_spot_x = 5 + (self.middle_x-5)*(self.info_flag%2) -5
        right_spot_x = self.middle_x + self.middle_x*(self.info_flag%2) +5
        up_spot_y = 5 + (self.middle_y-5)*(self.info_flag >= 2) - 5
        down_spot_y = self.middle_y + (self.middle_y)*(self.info_flag >= 2) + 5
        self.image_info = self.image_info[up_spot_y:down_spot_y,left_spot_x:right_spot_x]
        width = self.image_info.shape[1]       
 
        if(self.client_list[self.info_flag].disconnect_flag):
            time_s_str = self.client_list[self.info_flag].disconnect_time
            real_time_str = str(self.client_list[self.info_flag].disconnect_real_time)
        else:
            real_time_str = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())) 
            # set time_pass
            time_s_str = time.time() - self.client_list[self.info_flag].time_in
        time_str = ""
        time_m_str = int(time_s_str / 60)
        time_h_str = int(time_m_str / 60)
        if(time_h_str > 0):
            time_str = time_str + str(time_h_str) + " hours, "
        if(time_m_str > 0):
            time_str = time_str + str(time_m_str) + " mins, "
        time_str = time_str + str(int(time_s_str-3600*time_h_str-60*time_m_str))+" secs"
            
            
        # set info line
        info_line = "Name:"+str(self.client_list[self.info_flag].name.strip(' '))+", Number:"+str(self.client_list[self.info_flag].fire_num)
        info_line_img= np.zeros((100,width,3), np.uint8)
        info_line_img[:,:] = (255,255,255)
        cv2.putText(info_line_img,info_line,(10,40),cv2.FONT_HERSHEY_TRIPLEX,1, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(info_line_img,"Time_Pass: "+time_str+"    Real_Time: "+real_time_str,(10,80),cv2.FONT_HERSHEY_TRIPLEX,1, (0, 0, 0), 1, cv2.LINE_AA)
        
        # --draw image_info-- #
        self.image_info = np.concatenate((info_line_img,self.image_info),axis=0)

    def check_time(self):
        i = 0
        while i < 4:
            if(time.time() - self.client_list[i].time_in > self.time_to_come_out and self.connection_num[i]==1):
                if(self.client_list[i].over_time_flag):
                    pass
                else:
                    self.client_list[i].send_over_time_flag = True
                    msg = QMessageBox.question(self, 'Danger!!!!',"The FireFighter "+self.client_list[i].name.strip(' ')+" needs to come out !!!", QMessageBox.Ok | QMessageBox.Cancel,QMessageBox.Ok )
                    self.client_list[i].over_time_flag= True
            else:
                self.client_list[i].over_time_flag = False
                self.client_list[i].send_over_time_flag = False
            i += 1

    def add_no_wifi(self,index):
        line_left_spot_x = self.client_list[index].line_left_spot_x
        line_right_spot_x = self.client_list[index].line_right_spot_x
        line_up_spot_y = self.client_list[index].line_up_spot_y
        line_down_spot_y = self.client_list[index].line_down_spot_y
        if(self.client_list[index].disconnect_flag):
            temp_img = self.keep[line_up_spot_y:line_down_spot_y,line_left_spot_x:line_right_spot_x]
            self.no_wifi_image = cv2.resize(self.no_wifi_image,(temp_img.shape[1],temp_img.shape[0]))
            self.keep[line_up_spot_y:line_down_spot_y,line_left_spot_x:line_right_spot_x] = cv2.addWeighted(temp_img,0.5,self.no_wifi_image,0.5,0)
        else:  
            pass


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())

