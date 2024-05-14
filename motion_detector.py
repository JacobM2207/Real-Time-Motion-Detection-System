#Final Project: Motion Sensor Alarm System

from machine import Pin, SoftI2C, Timer
import network
import urequests
import json
import ujson

#Webhooks information
HTTP_HEADERS = {'Content-Type': 'application/json'}

#global Pins
red_led = Pin(21, Pin.OUT)
green_led = Pin(14, Pin.OUT)
#Flags
Active = False
send_notification_flag = False
#location of the mpu
mpu6050 = 0x68
config_reg = 0x1C

#location of the sensor for x,y, and z
Xout = 0x3B
Yout = 0x3D
Zout = 0x3F

#initialize Comms
i2c = SoftI2C(scl=Pin(22), sda=Pin(23), freq=400000)

def wifi_setup():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.scan()
    if not wlan.isconnected():
        print('connecting to network...')
        print('')
        wlan.connect('Wifi', 'Password')
        while not wlan.isconnected():
            pass
    info = wlan.ifconfig()
    print("Connected to Wifi")
    print(f"IP Address: {info[2]}")
    print('')

#function to convert byte data to decimal
def bytes_to_int(data):
    if not data[0] & 0x80:
        return data[0] << 8 | data[1]
    return -(((data[0] ^ 0xFF) << 8) | (data[1] ^ 0xFF) + 1)

#Function to read from register
def read_register(reg):
    i2c.start()
    data = i2c.readfrom_mem(mpu6050, reg, 2)
    i2c.stop()
    signed_data = bytes_to_int(data)
    value = signed_data/16384 * 9.81
    return value

#Function to read from SpeakThings
def read_server():
    url = 'Enter Thing Speak API Key'
    r = urequests.get(url)
    data = json.loads(r.text)
    r3= data["feeds"][0]["field1"]
    r4= data["feeds"][1]["field1"]
    return r3, r4

#function to send notification to phone
def send_notification(x, y, z):
    url= 'Enter IFTT API Key'
    payload = ujson.dumps({"value1" : x, "value2": y, "value3" : z})
    response = urequests.post(url, data=payload, headers = HTTP_HEADERS)
    response.close()
    
def accel_read(time0): #checks to see if the system is armed
    global Active
    data, data1 = read_server() # looks at the last two data points sent to SpeakThings
    #print(data1)
    if int(data1) == 5:
        Active = True
    else:
        Active = False
    return Active

#determines if motion is detected
def motion_detected(x, y, z):
    if x > 2 or y > 2 or z > 10:
        return True
    elif x < -2 or y < -2 or z < 7:
        return True
    else:
        return False

def notification_window_callback(time1):
    global notification_window
    notification_window = False
    
def send_notification_callback(time2):
    global send_notification_flag
    send_notification_flag = True

#Main Function
def main():
    global Active
    global send_notification_flag
    
    count = 0
    wifi_setup() #setup wifi connection
    
    time0 = Timer(0) #setup timer to check if system is armed
    time0.init(period = 30000, mode = Timer.PERIODIC, callback= accel_read)
    
    time2 = Timer(2)#Timer that allows notifications to be sent every 10 seconds
    time2.init(period=10500, mode = Timer.PERIODIC, callback = send_notification_callback)
    
    i2c.writeto(0x68, bytearray([107, 0]))
    
    try:
        while True:
            green_led.value(0)
            red_led.value(0)

            
            while Active:
                #print("Motion Sensor Activated")
                green_led.value(1)
                x_accel = read_register(Xout)
                y_accel = read_register(Yout)
                z_accel = read_register(Zout)
                
            
                if motion_detected(x_accel, y_accel, z_accel): #if motion is detected
                    red_led.value(1)

                    #time2 = Timer(2)#Timer that allows notifications to be sent every 10 seconds
                    #time2.init(period=10000, mode = Timer.PERIODIC, callback = send_notification_callback)

                    if send_notification_flag:
                        if count <= 5: #A notification is only sent every 10 seconds no longer than a minute
                            send_notification(x_accel, y_accel, z_accel)
                            print("notification sent")
                            send_notification_flag = False
                            count += 1
                        else:
                            print("no notification sent")
                            time2.deinit()  
                    
                    else:
                        pass

                else:
                    red_led.value(0)
                    count = 0
    
    except KeyboardInterrupt:
        pass
    
if __name__=="__main__":
    main()
    