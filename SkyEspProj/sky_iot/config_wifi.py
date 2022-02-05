import os
import time
import network
import sky_iot.globalvar as gl
from socket import *
from sky_iot.led import device_led

class ConfigWifi:
    def __init__(self):
        self.ap_if = network.WLAN(network.AP_IF)
        self.ap_if.active(False)
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(False)

        self.__wifi_init()

    def __wifi_init(self):
        if self.wifi_isconnect() == True:
            self.sta_if.active(False)
        # LED指示灯
        device_led.led_off()
        # 热点信息
        self.wifi_ssid = gl.get_value("config")['wifiConfig']['ssid'].strip()
        self.wifi_passwd = gl.get_value("config")['wifiConfig']['password'].strip()
        print("SSID: ", self.wifi_ssid, "PASSWD: ", self.wifi_passwd)
        # AP配网
        self.ap_ssid = gl.get_value("config")['deviceConfig']['apname']
        self.ap_passwd = gl.get_value("config")['deviceConfig']['appasswd']

    def __wifi_ap_init(self):
        self.ap_if = network.WLAN(network.AP_IF)
        self.ap_if.active(True)
        self.ap_if.config(essid=self.ap_ssid, password=self.ap_passwd)
        print('The AP build......')
        for i in range(5):
            time.sleep(1)
        print(self.ap_if.ifconfig())
        print("The AP was created successfully!")
        device_led.led_on() # led常亮表示连接热点失败，开启AP配网模式

        self.__wifi_recv_params(self.ap_if) # 等待接收配网数据

    def wifi_connect(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(True)
        self.sta_if.scan()
        self.sta_if.connect(self.wifi_ssid,self.wifi_passwd)
        for i in range(5):
            device_led.led_blink(0.5, 1) # led灯闪烁表示正在尝试连接wifi
            print(i+1,'Attempt at connection...')
        if self.sta_if.isconnected()==True:
            print("Wifi connection successful!", self.sta_if.ifconfig())
            return True
        else:
            print("Wifi connection failed!")
            self.sta_if.active(False)
            return False

    def __wifi_recv_params(self, ap):
        bind_ip = "192.168.4.1"
        bind_port = 8888

        udp_socket=socket(AF_INET,SOCK_DGRAM)
        local_addr=(bind_ip,bind_port) #ip地址和端口号，IP不写表示本机任何一个ip
        udp_socket.bind(local_addr) #等待接收对方发送的数据

        while True:
            data,addr=udp_socket.recvfrom(1024) #1024表示本次接收的最大字节
            print("Data: ", data, "Addr: ", addr)
            recv_msg = data.decode("gbk")
            try:
                recv_msg = recv_msg.split(",", 1) # 按逗号分割
                print(recv_msg)

                self.wifi_ssid = recv_msg[0].strip()
                self.wifi_passwd = recv_msg[1].strip()
                udp_socket.close()
                break
            except:
                print("Recv data parse error!")

            time.sleep(0.2)

        # 关闭AP模式，尝试连接热点
        ap.active(False)
        self.wifi_init()

    def wifi_isconnect(self):
        return self.sta_if.isconnected()

    def wifi_init(self, reset=False):
        if reset == True:
            self.__wifi_init() # 初始化wifi信息
        if self.wifi_connect() == True:
            # 连接成功，写入wifi信息
            ssid = gl.get_value("config")['wifiConfig']['ssid'].strip()
            passwd = gl.get_value("config")['wifiConfig']['password'].strip()

            if ssid != self.wifi_ssid or passwd != self.wifi_passwd:
                gl.get_value("config")['wifiConfig']['ssid'] = self.wifi_ssid
                gl.get_value("config")['wifiConfig']['password'] = self.wifi_passwd
                gl.save_config(gl.get_value("config")) # 保存配置
            print("Wifi connected!")
        else:
            # 开启AP模式进行配网
            self.__wifi_ap_init()

    
