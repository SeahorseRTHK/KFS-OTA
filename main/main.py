# KFS-Tilapia-SmartCam - By: Reuben Tan - Sat Jul 21 2022
#
# Thanks to Mobizt, and fustyles for their Line Notify related repositories on Github
#

import network, usocket, ussl, sensor, image, machine, senko
from mqtt import MQTTClient

GithubURL = "https://github.com/SeahorseRTHK/KFS-OTA/blob/main/main/"
OTA = senko.Senko(url=GithubURL, files=["main.py","openmv.config","senko.py"])

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.UXGA)   # Set frame size
sensor.skip_frames(time = 2000)     # Wait for settings take effect.

PORT = 443
HOST = "notify-api.line.me"
token = "qBx4XoGPSJU9zxy3tYLBnbt31AFVVGXD35GC6nlJr28"

# AP info
#SSID="SEAHORSE@unifi" # Network SSID
#KEY="SH42827AU"  # Network key
SSID="Seahorse"
KEY="789456123"

# Init wlan module and connect to network
print("Trying to connect... (may take a while)...")

wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)

# We should have a valid IP now via DHCP
print(wlan.ifconfig())

# LINE
# Get addr info via DNS
addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
print(addr)

# MQTT
# Set keepalive or else it will fail
mainTopic = "OpenMV"
MQTT = MQTTClient(mainTopic, "honwis.dyndns.biz", port=1883, keepalive=100)
MQTT.connect()
MQTT.connect()
# MQTT callbacks
def callback(topic, msg):
    print(topic, msg)
    if msg == b'image' or msg == b'photo':
        sensor.set_framesize(sensor.QVGA)
        sensor.set_windowing(240,240)
        img = sensor.snapshot().compress(quality=50)
        base64 = ubinascii.b2a_base64(img)
        MQTT.publish("86Box/Photo", base64)
        #wlan.disconnect()
        #wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
        #print(wlan.ifconfig())
        #MQTT.disconnect()
        MQTT.connect()
        del img
        del base64
    if msg == b'checkver':
        print("Check update")
        if OTA.fetch():
            print("A newer version is available!")
        else:
            print("Up to date!")
    if msg == b'update':
        print("Checking for new version")
        if OTA.fetch():
            print("A newer version is available!")
            print("Updating")
            if OTA.update():
                print("Updated to the latest version! Rebooting...")
                machine.reset()
            else:
                print("Not updated!")
        else:
            print("Already up to date! Not updating")


        print("Reset")
        machine.reset()
        print("Not supposed to show")
# must set callback first
MQTT.set_callback(callback)
MQTT.subscribe(mainTopic + "/command")
MQTT.publish(mainTopic, "OpenMV ONLINE!")

def sendMQTT(subTopic, msg):
    subTopic = mainTopic + "/" + subTopic
    MQTT.publish(subTopic, msg)

def sendLINE(msg):
    # LINE Notify
    # Create a new socket and connect to addr
    LINE_Notify = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    LINE_Notify.connect(addr)
    # Set timeout
    LINE_Notify.settimeout(3.0)
    # Set ssl
    LINE_Notify = ussl.wrap_socket(LINE_Notify, server_hostname=HOST)

    if msg is None:
        message = "OpenMV-CAM"
    else:
        message = msg

    sensor.set_framesize(sensor.UXGA)
    sensor.set_windowing(1600,1200)
    head = "--Taiwan\r\nContent-Disposition: form-data; name=\"message\"; \r\n\r\n" + message + "\r\n--Taiwan\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"OpenMV-CAM.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n"
    tail = "\r\n--Taiwan--\r\n"
    img = sensor.snapshot().compress(quality=95)
    #print(img.bytearray())
    # Convert to base64
    #base64 = ubinascii.b2a_base64(img)
    #print(base64)

    # Calculate message length
    totalLen = str(len(head) + len(tail) + len(img.bytearray()))
    print("totalLen is " + totalLen)

    # Send HTTP request and read response
    # Headers
    request = "POST /api/notify HTTP/1.1\r\n"
    request += "cache-control: no-cache\r\n"
    request += "Authorization: Bearer " + token + "\r\n"
    request += "Content-Type: multipart/form-data; boundary=Taiwan\r\n"
    request += "User-Agent: OpenMV\r\n"
    request += "Accept: */*\r\n"
    request += "HOST: " + HOST + "\r\n"
    request += "accept-encoding: gzip, deflate\r\n"
    request += "Connection: close\r\n"
    request += "Content-Length: " + totalLen + "\r\n"
    request += "\r\n"
    # Add more headers if needed.

    print("")
    print("headers are ")
    print("")
    print(request)
    print("")
    print("body is ")
    print(head)
    print(tail)
    print("")
    LINE_Notify.write(request)
    LINE_Notify.write(head)
    LINE_Notify.write(img.bytearray())
    LINE_Notify.write(tail)
    del img
    gc.collect()
    #del base64
    print(LINE_Notify.read())
    print("")

    # Close socket when done
    LINE_Notify.close()

while (wlan.isconnected() == True):
    #try:
    print("Waiting")
    MQTT.wait_msg()
    time.sleep_ms(1000)
    #except:
        #MQTT.disconnect()
        #MQTT.connect()
        #print("Checkpoint")

else:
    print("WiFi not connected, connecting")
    wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)

    # We should have a valid IP now via DHCP
    print(wlan.ifconfig())

    # LINE
    # Get addr info via DNS
    addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
    print(addr)

    #MQTT
    MQTT.connect()
    MQTT.set_callback(callback)
    MQTT.subscribe(mainTopic + "/command")
    MQTT.publish(mainTopic, "OpenMV ONLINE!")
