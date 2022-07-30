Version = "v1.5"
import os, network, usocket, ussl, sensor, image, machine, time, gc, micropython, senko
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
SSID="Seahorse"
KEY="789456123"
print("Trying to connect... (may take a while)...")
wlan = network.WINC()
try:
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
except OSError:
	print("Failed to connect to WiFi, trying again after 3 seconds")
	time.sleep(3.0)
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
except:
	print("Failed again, restarting")
	machine.reset()
try:
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
except OSError:
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
except:
	machine.reset()
mainTopic = "OpenMV"
MQTT = MQTTClient(mainTopic, "honwis.dyndns.biz", port=1883, keepalive=65500)
try:
	print("Connecting to MQTT server")
	MQTT.connect()
	print("Connected to MQTT server")
except OSError:
	print("Failed to connect to MQTT server, trying again after 3 seconds")
	time.sleep(3.0)
	MQTT.connect()
	print("Connected to MQTT server")
except:
	print("doing machine reset")
	machine.reset()
def callback(topic, msg):
	print(topic, msg)
	if msg == b'details':
		f = open("camInfo.txt", "r")
		info = f.read()
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
def sendMQTT(subTopic, msg):
	subTopic = mainTopic + "/" + subTopic
	MQTT.publish(subTopic, msg)
def sendLINEmsg(msg):
	LINE_Notify = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
	LINE_Notify.connect(addr)
	LINE_Notify.settimeout(5.0)
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
	LINE_Notify.settimeout(5.0)
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
try:
	print("Reading file")
	f = open("camInfo.txt", "r")
	message = f.read()
	f.close()
	print("message is " + message)
except OSError:
	print("OSError 2 ENOENT = file/dir does not exist, creating file")
	f = open("camInfo.txt", "w")
	f.write("cam:no-setting-is-available")
	message = "cam:no-setting-is-available"
	print("Created new camInfo.txt file with cam:no-setting-is-available")
	f.close()
finally:
	MQTT.publish(mainTopic, message + " is online")
	sendLINEmsg(message + " is online")
	time.sleep_ms(500)
f = open("camInfo.txt", "r")
temp = f.read(4)
message = f.read()
f.close()
print("temp is " + temp)
print("message is " + message)
if temp == "cam:":
	if (temp+message) == "cam:no-setting-is-available":
		print("Preparing camera to read QR codes")
		sensor.set_pixformat(sensor.GRAYSCALE)
		sensor.set_framesize(sensor.VGA)
		sensor.skip_frames(time = 2000)
		sensor.set_auto_gain(False)
		sendLINEmsg("Camera ready to read QR code")
		time.sleep_ms(2000)
		print("No setting, scanning for QR code")
		while (temp+message) == "cam:no-setting-is-available":
			img = sensor.snapshot()
			img.lens_corr(1.8)
			for code in img.find_qrcodes():
				img.draw_rectangle(code.rect(), color = (255, 0, 0))
				print(code)
				read = code.payload()
				print("code.payload is " + read)
				sendLINEmsg("QR code scanned: " + read + ". Restarting device with new settings")
				f = open("camInfo.txt", "w")
				f.write(read)
				f.close()
				print("Set, restarting")
			del img
			time.sleep_ms(500)
	else:
		info = message.split("-")
		print(info)
		print(len(info))
		for x in info:
			print(x)
else:
	sendLINEmsg("Setting is " + temp + message + ". Wrong setting, please set again. Restarting")
	f = open("camInfo.txt", "w")
	f.write("cam:no-setting-is-available")
	f.close()
	machine.reset()
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