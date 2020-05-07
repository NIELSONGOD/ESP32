'''
实验名称：阿里云物联网平台温湿度传感器应用
版本：v1.0
日期：2019.12
作者：NL
说明：WZ_ESP32通过socket通信，连接本地PC，周期性上报温度、湿度数据。
'''

import network, socket, time
from machine import I2C, Pin, Timer
import json
from ssd1306 import SHT_I2C
from ssd1306 import SSD1306_I2C

# 初始化相关模块，实例化SSD1306_I2C
i2c = I2C(sda=Pin(14), scl=Pin(13))
oled = SSD1306_I2C(128, 32, i2c, addr=0x3c)
i2c_sht = I2C(scl=Pin(5), sda=Pin(26), freq=100000)  # I2C初始化：sda--> 26, scl --> 5，频率100k
sht = SHT_I2C(i2c_sht, addr=0x44)  # 实例化sht

led = Pin(23, Pin.OUT)
beep = Pin(27, Pin.OUT, 0)  # 低电平输出

'''
# WIFI连接函数
def WIFI_Connect():
    global wlan
    wlan = network.WLAN(network.STA_IF)  # STA模式
    wlan.active(True)  # 激活接口
    start_time = time.time()  # 记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Guest-WZ', 'gjbgjbgjb')  # 输入WIFI账号密码

        while not wlan.isconnected():

            # LED闪烁提示
            led.value(1)
            time.sleep_ms(300)
            led.value(0)
            time.sleep_ms(300)

            # 超时判断,15秒没连接成功判定为超时
            if time.time() - start_time > 15:
                print('WIFI Connected Timeout!')
                break

    if wlan.isconnected():
        # LED点亮
        led.value(1)

        # 串口打印信息
        print('network information:', wlan.ifconfig())

        # OLED数据显示（如果没接OLED，请将下面代码屏蔽）
        oled.fill(0)  # 清屏背景黑色
        oled.text('IP/Subnet/GW:', 0, 0)
        oled.text(wlan.ifconfig()[0], 0, 20)
        oled.text(wlan.ifconfig()[1], 0, 38)
        oled.text(wlan.ifconfig()[2], 0, 56)
        oled.show()

        return True

    else:
        return False
'''


def Socket_fun(tim):
    text = conn.recv(1024)  # 单次最多接收128字节
    if text == None:
        pass

    else:  # 打印接收到的信息为字节，可以通过decode('utf-8')转成字符串
        print(text.decode('utf-8'))

        if text[4] == 0x31:
            led.value(0)
            beep.value(1)
        else:
            led.value(1)
            beep.value(0)

'''

# 执行WIFI连接函数并判断是否已经连接成功
if WIFI_Connect():

    port = 80
    listenSocket = None
    ip = wlan.ifconfig()[0]

    listenSocket = socket.socket()  # 建立一个实例
    listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenSocket.bind((ip, port))  # 绑定建立网路连接的ip地址和端口
    print('bind success')
    listenSocket.listen(5)  # 开始侦听
    print('listen start')
    print("wait connectting.....")
    conn, addr = listenSocket.accept()
    print("connected %s" % str(addr))

    #开启RTOS定时器，编号为-1,周期300ms，执行socket通信接收任务
    tim = Timer(-1)

    tim.init(period=500, mode=Timer.PERIODIC,callback=Socket_fun)
'''

wlan = network.WLAN(network.AP_IF)  # AP模式
wlan.active(False)
wlan.active(True)  # 激活接口

wlan.ifconfig(['192.168.4.1', '255.255.255.0', '192.168.0.254', '114.114.114.114'])
wlan.config(essid='WZ_ESP32', channel=1, authmode=0, password='55667788')

print('network ifconfig:', wlan.ifconfig())
print('wifi channel:', wlan.config('channel'))

time.sleep(1)

port = 80
listenSocket = None
ip = wlan.ifconfig()[0]

listenSocket = socket.socket()  # 建立一个实例
listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listenSocket.bind((ip, port))  # 绑定建立网路连接的ip地址和端口
print('bind success')
listenSocket.listen(5)  # 开始侦听
print('listen start')
print("wait connectting.....")
conn, addr = listenSocket.accept()
print("connected %s" % str(addr))

# 开启RTOS定时器，编号为-1,周期300ms，执行socket通信接收任务
tim = Timer(-1)

tim.init(period=500, mode=Timer.PERIODIC, callback=Socket_fun)

while True:
    data = conn.recv(128)

    numbers1 = int(data[2])
    numbers2 = int(data[3])
    print(numbers1)
    print(numbers2)

    # print(str(data))

    oled.fill(0)  # 清屏背景黑色
    # oled.text('IP/Subnet/GW:', 0, 0)
    oled.text(str(data), 0, 2)
    oled.show()
    # time.sleep(1)
