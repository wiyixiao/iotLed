import time
from machine import Pin

class Led:
    def __init__(self, pin):
        self.led_pin = pin
        self.led = Pin(self.led_pin, Pin.OUT)

    def led_on(self):
        self.led.value(0)
        pass

    def led_off(self):
        self.led.value(1)
        pass

    ''' LED灯闪烁
    :param t 闪烁间隔
    :param n 闪烁次数
    :return:
    '''
    def led_blink(self, t, n):
        while n > 0:
            self.led_on()
            time.sleep(t)
            self.led_off()
            time.sleep(t)
            n-=1
        pass
 
device_led = Led(2)
device_led.led_on()
