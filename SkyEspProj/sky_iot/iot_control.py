import json
import time
import sky_iot.globalvar as gl
from machine import UART
from sky_iot.led import device_led
from machine import Pin, PWM
from sky_iot.utils import UtilsTool

class Servo:
    def __init__(self, pin):
        self.pin = pin
        self.last_angle = gl.get_value("config")['settingMsg']['led']['wait'] # 初始角度
        # Pin(self.pin, Pin.OUT)
        pass

    def attach(self):
        self.pwm = PWM(Pin(self.pin))
        pass

    def write(self, angle):
        self.pwm.freq(50)
        duty = int(UtilsTool.rang_map(angle, 0, 270, 0.5, 2.5)/20*1023) # 20ms周期 0.5~2.5ms 对应 0 ~270度
        self.pwm.duty(duty)
        pass

    def write_target(self, target, speed):
        device_led.led_on() # 指示灯亮
        self.attach()
        step = 1
        m_target = target
        if target < self.last_angle:
            step = -1

        m_target += step

        for angle in range(self.last_angle, m_target, step):
            self.write(angle)
            time.sleep(speed)
        self.detach()
        self.last_angle = target
        device_led.led_off() # 设置完成，指示灯灭
        pass

    def detach(self):
        self.pwm.deinit()

class DeviceConfig:
    def __init__(self):
        self.servo = Servo(0)
        self.servo.attach()

    def init(self):
        # self.servo.write_target(gl.get_value("config")['settingMsg']['led']['wait'], 0.005) # 初始角度
        pass

    def light_set(self, data):
        obj = json.loads(data)
        state = obj['state'].strip()
        if state == 'on' or state == 'off':
            self.servo.write_target(gl.get_value("config")['settingMsg']['led'][state], 0.005) # 控制开关的舵机
            # self.servo.write(gl.get_value("config")['settingMsg']['led'][state]) # 控制开关的舵机
            
        time.sleep(0.5)
        self.servo.write_target(gl.get_value("config")['settingMsg']['led']['wait'], 0.005) # 恢复初始角度
        # self.servo.write(gl.get_value("config")['settingMsg']['led']['wait']) # 恢复初始角度
        pass

    def stepmotor_set(self, data):
        pass

class IotControl:
    def __init__(self, en=False):
        self.uart = None
        self.server = None
        self.enable = en
        self.device = DeviceConfig()
        pass

    def init(self, server, reset_callback):
        self.server = server # 传入mqtt服务
        self.device.init()
        self.reset_cb = reset_callback
        if self.enable == True:
            self.uart = UART(0, baudrate=115200)

    def iot_parse_msg(self,tp,msg):
        # print((tp, msg))
        str = tp.decode().strip()
        data = msg.decode().strip()

        if str.startswith(gl.get_value("topics")['control']): # 控制命令
            if str.endswith('led'):
                self.device.light_set(data)
                pass
            elif str.endswith('stepmotor'):
                self.device.stepmotor_set(data)
                pass
            pass
        elif str.startswith(gl.get_value("topics")['setting']): # 读写配置命令
            if str.endswith('r'):
                self.server.mqtt_push_msg(b'settingMsg', json.dumps(gl.get_value("config")).encode())
                pass
            elif str.endswith('w'):
                print("Config reset...")
                gl.save_config(json.loads(data))
                self.reset_cb() # 配置写入完成回调，重置设备
                pass
            pass

    def iot_send_data(self):
        if self.enable == True:
            self.uart.write(b'hello skyiot\n')
        pass

iot_controller = IotControl(False) # 使能开启uart0