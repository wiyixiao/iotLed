import os
import time
import sky_iot.globalvar as gl
from machine import Timer
from sky_iot.config_wifi import ConfigWifi
from sky_iot.config_mqtt import ConfigMqtt
from sky_iot.iot_control import iot_controller

# mqtt 消息回调
def mqtt_sub_cb(topic, msg):
    iot_controller.iot_parse_msg(topic, msg) # 解析消息

#实例化对象
device_wifi = ConfigWifi()
device_mqtt = ConfigMqtt(mqtt_sub_cb)
t = Timer(1)

wifi_connect_flag = False # wifi连接状态
reset_flag = False # 配置重置

# 配置修改回调
def reset_cb():
    global reset_flag
    reset_flag = True;
    pass

def timer_task(t):
    global wifi_connect_flag
    wifi_connect_flag = device_wifi.wifi_isconnect()

def iot_welcome():
    print("********************************************")
    print("Welcome to Sky IOT System!")
    print("Version: ", gl.get_value("config")["deviceConfig"]["version"])

def iot_init():
    print("System init...5(s)")
    global wifi_connect_flag, reset_flag
    time.sleep(5) # 等待3s
    device_wifi.wifi_init(reset_flag)
    wifi_connect_flag = device_wifi.wifi_isconnect()

    if wifi_connect_flag == True:
        device_mqtt.mqtt_init()
        iot_controller.init(device_mqtt, reset_cb) # 连接成功，初始化串口，使能uart0
        device_mqtt.mqtt_connect()
        # 开启一个定时任务
        t.init(period=1000,mode=Timer.PERIODIC,callback=timer_task)
    pass

def iot_run():
    global wifi_connect_flag, reset_flag
    iot_welcome()
    iot_init()
    while True:
        if reset_flag == True:
            device_mqtt.mqtt_disconnect() # 断开连接
            iot_init()
            print("Config reset successful")
            reset_flag = False
        if wifi_connect_flag == False:
            wifi_connect_flag = device_wifi.wifi_connect()
        time.sleep(1)
        device_mqtt.mqtt_reconnect() # 自动重连检测

