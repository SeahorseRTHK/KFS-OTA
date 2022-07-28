Version = "v1.2"
import network, usocket, ussl, sensor, image, machine, time, gc, micropython, senko
from mqtt import MQTTClient
GithubURL = "https://github.com/SeahorseRTHK/KFS-OTA/blob/main/main/"
OTA = senko.Senko(user="SeahorseRTHK", repo="KFS-OTA", working_dir="main", files=["main.py"])
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.UXGA)
sensor.skip_frames(time = 2000)
PORT = 443
HOST = "notify-api.line.me"
token = "qBx4XoGPSJU9zxy3tYLBnbt31AFVVGXD35GC6nlJr28"
SSID="SEAHORSE@unifi"
KEY="SH42827AU"
print("Trying to connect... (may take a while)...")
wlan = network.WINC()
try:
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
except:
	print("Failed to connect to WiFi, trying again after 3 seconds")
	time.sleep(3.0)
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
try:
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
except:
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
mainTopic = "OpenMV"
MQTT = MQTTClient(mainTopic, "honwis.dyndns.biz", port=1883, keepalive=65500)
try:
	print("Connecting to MQTT server")
	MQTT.connect()
	print("Connected to MQTT server")
except:
	print("Failed to connect to MQTT server, trying again after 3 seconds")
	time.sleep(3.0)
	MQTT.connect()
	print("Connected to MQTT server")
def callback(topic, msg):
	print(topic, msg)
	if msg == b'details':
		message = "OpenMV-CAM " + Version
		sendLINEmsg(message)
	if msg == b'lineimage' or msg == b'linephoto':
		message = "OpenMV-CAM " + Version + ", photo"
		sendLINEphoto(message)
	if msg == b'mqttimage' or msg == b'mqttphoto':
		sensor.set_framesize(sensor.QVGA)
		sensor.set_windowing(240,240)
		img = sensor.snapshot().compress(quality=50)
		MQTT.publish("86Box/Photo", img)
		del img
	if msg == b'update':
		print("Updating")
		try:
			print("Try")
			micropython.mem_info()
			if OTA.update():
				print("Updated to the latest version! Rebooting...")
				machine.reset()
		except:
			print("Except")
			micropython.mem_info()
			print("Not updated!")
MQTT.set_callback(callback)
MQTT.subscribe(mainTopic + "/command")
MQTT.publish(mainTopic, "OpenMV ONLINE!")
def sendMQTT(subTopic, msg):
	subTopic = mainTopic + "/" + subTopic
	MQTT.publish(subTopic, msg)
def sendLINEmsg(msg):
	LINE_Notify = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
	LINE_Notify.connect(addr)
	LINE_Notify.settimeout(3.0)
	LINE_Notify = ussl.wrap_socket(LINE_Notify, server_hostname=HOST)
	head = "--Taiwan\r\nContent-Disposition: form-data; name=\"message\"; \r\n\r\n" + msg
	print("len of head is " + str(len(head)))
	tail = "\r\n--Taiwan--\r\n"
	print("len of tail is " + str(len(tail)))
	totalLen = str(len(head) + len(tail))
	print("totalLen is " + totalLen)
	print("head is " + head)
	print("tail is " + tail)
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
	LINE_Notify.write(request)
	LINE_Notify.write(head)
	LINE_Notify.write(tail)
	print(LINE_Notify.read())
	gc.collect()
	LINE_Notify.close()
def sendLINEphoto(msg):
	LINE_Notify = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
	LINE_Notify.connect(addr)
	LINE_Notify.settimeout(3.0)
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
	totalLen = str(len(head) + len(tail) + len(img.bytearray()))
	print("totalLen is " + totalLen)
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
	print(LINE_Notify.read())
	print("")
	LINE_Notify.close()
while (wlan.isconnected() == True):
	print("waiting")
	MQTT.wait_msg()
else:
	print("WiFi not connected, connecting")
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
	MQTT.connect()
	MQTT.set_callback(callback)
	MQTT.subscribe(mainTopic + "/command")
	MQTT.publish(mainTopic, "OpenMV ONLINE!")