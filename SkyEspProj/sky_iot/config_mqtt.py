import utime
import time
import json
import micropython
import sky_iot.globalvar as gl
from .umqtt.simple import MQTTClient
from sky_iot.led import device_led

class ConfigMqtt:
    def __init__(self, sub_cb):
        self.sub_cb = sub_cb
        self.detect_count = 0
        self.connect_flag = False
        pass

    def mqtt_init(self):
        self.c = MQTTClient(client_id=gl.get_value("config")["deviceConfig"]["clientid"],
            server=gl.get_value("config")["deviceConfig"]["server"],
            port=gl.get_value("config")["deviceConfig"]["port"],
            user=gl.get_value("config")["deviceConfig"]["user"],
            password=gl.get_value("config")["deviceConfig"]["passwd"],
            keepalive=gl.get_value("config")["deviceConfig"]["keepalive"],
            ssl=gl.get_value("config")["deviceConfig"]["ssl"],
            # ssl_params=gl.get_value("config")["deviceConfig"]["sslparams"]
        )
        self.c.set_callback(self.sub_cb) # 设置消息回调
        self.detect_count = 0
        self.connect_flag = False
        self.time_begin = utime.mktime(utime.localtime())
        pass

    def mqtt_connect(self):
        try:    
            if self.c.connect() == 0:
                self.connect_flag = True
                self.c.subscribe((gl.get_value("topics")["control"] + '+').encode()) # 控制消息
                self.c.subscribe((gl.get_value("topics")["setting"] + '+').encode()) # 配置读写 r | w
                print("Connect to mqtt server successful")
                return True
        except:
            print("Connect to mqtt server failed")
            return False

    def mqtt_disconnect(self):
        try:
            if self.connect_flag == True:
                self.c.disconnect()
        except:
            print("Mqtt disconnect error!")

    def __reconnect(self):
        self.mqtt_disconnect()
        print("Retry connect to mqtt server...")
        return self.mqtt_connect()

    # 检测是否断开连接任务
    def mqtt_reconnect(self):
        try:
            if self.detect_count >= 20: # 检测一次
                # print("Connected detect...")
                device_led.led_blink(0.1, 1)
                stamp = (utime.mktime(utime.localtime()) - self.time_begin)
                gl.get_value("config")['uploadMsg']['runtime'] = stamp
                self.mqtt_push_msg(b"uploadMsg", json.dumps(gl.get_value("config")['uploadMsg']).encode())
                self.detect_count = 0
                self.c.ping()
            else:
                if self.connect_flag == False:
                    device_led.led_blink(0.05, 1)
                    return self.__reconnect()
                self.c.check_msg()
                self.detect_count += 1
        except Exception as e: # 连接丢失
            print(e)
            self.connect_flag = False
            device_led.led_blink(0.05, 1)
            return self.__reconnect()
        else:
            pass

    def mqtt_push_msg(self, tp, msg):
        self.c.publish(tp, msg)
