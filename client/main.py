'''
实验名称：阿里云物联网平台温湿度传感器应用
版本：v1.0
日期：2019.12
作者：NL
说明：WZ_ESP32通过socket通信，连接本地PC，周期性上报温度、湿度数据。
'''

import network,usocket,time
from machine import I2C, Pin, Timer
from ssd1306 import SHT_I2C
from ssd1306 import SSD1306_I2C

# 初始化相关模块
i2c = I2C(sda=Pin(14), scl=Pin(13))
oled = SSD1306_I2C(128, 32, i2c, addr=0x3c)
i2c_sht = I2C(scl=Pin(5), sda=Pin(26), freq=100000)  # I2C初始化：sda--> 19, scl --> 18，频率100k
sht = SHT_I2C(i2c_sht, addr=0x44)  # 实例化sht

wlan = network.WLAN(network.STA_IF)  # STA模式
#wlan.disconnect()  # 断开之前的WIFI连接


# WIFI连接函数
def WIFI_Connect():
    global wlan
    WIFI_LED = Pin(23, Pin.OUT)  # 初始化WIFI指示灯
    wlan.active(True)  # 激活接口
    start_time = time.time()  # 记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('WZ_ESP32', '')  # 输入WIFI账号密码
        wlan.ifconfig(['192.168.4.2', '255.255.255.0', '192.168.0.254', '114.114.114.114'])
        # wlan.connect('MERCURY_66D6', '')
        while not wlan.isconnected():

            # LED闪烁提示
            WIFI_LED.value(1)
            time.sleep_ms(300)
            WIFI_LED.value(0)
            time.sleep_ms(300)

            # 超时判断,15秒没连接成功判定为超时
            if time.time() - start_time > 15:
                print('WIFI Connected Timeout!')
                break

    if wlan.isconnected():
        # LED点亮
        WIFI_LED.value(1)

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


def Socket_fun(tim):
    sht.read()

    ftem = (175 * (SHT_I2C.data[0] * 256 + SHT_I2C.data[1]) / 65535 - 45)
    item = int(175 * (SHT_I2C.data[0] * 256 + SHT_I2C.data[1]) / 65535 - 45)
    hum = int(100 * (SHT_I2C.data[3] * 256 + SHT_I2C.data[4]) / 65535)
    if item >= 24:
        key = 1
    else :
        key = 0
    # OLED显示温湿度
    oled.fill(0)  # 清屏背景黑色
    oled.text('WZ_ESP32', 0, 0)
    oled.text('SHT32 test:', 0, 12)
    oled.text("T: " + str(item), 0, 25)  # 温度显示
    oled.text("H: " + str(hum), 48, 25)  # 湿度显示
    oled.show()
    s.sendall(str(item)+str(hum)+str(key))

    '''
    text=s.recv(128) #单次最多接收128字节
    if text == '':
        s.send("hello WZ")

    else: #打印接收到的信息为字节，可以通过decode('utf-8')转成字符串
        print(text)
        s.send('I got:'+text.decode('utf-8'))
    '''



# 执行WIFI连接函数并判断是否已经连接成功
if WIFI_Connect():
    sht.wake()
    time.sleep(1)
    #创建socket连接TCP类似，连接成功后发送“Hello WZ！”给服务器。
    s=usocket.socket()
    addr=('192.168.4.1',80) #服务器IP和端口
    s.connect(addr)
    s.send('Hello WZ_ESP32!')

    #开启RTOS定时器，编号为-1,周期500ms，执行socket通信接收任务
    tim = Timer(-1)
    tim.init(period=500, mode=Timer.PERIODIC,callback=Socket_fun)

