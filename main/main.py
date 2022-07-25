from ota_updater import OTAUpdater
def download_and_install_update_if_available():
	ota_updater = OTAUpdater('https://github.com/SeahorseRTHK/KFS-OTA', main_dir = 'main')
	ota_updater.install_update_if_available_after_boot("Seahorse", "789456123")
def start():
	import network, usocket, ussl, sensor, image, machine
	from mqtt import MQTTClient
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
	wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)
	print(wlan.ifconfig())
	addr = usocket.getaddrinfo(HOST, PORT)[0][-1]
	print(addr)
	mainTopic = "OpenMV"
	MQTT = MQTTClient(mainTopic, "honwis.dyndns.biz", port=1883, keepalive=100)
	MQTT.connect()
	MQTT.connect()
	def callback(topic, msg):
		print(topic, msg)
		if msg == b'image' or msg == b'photo':
			sensor.set_framesize(sensor.QVGA)
			sensor.set_windowing(240,240)
			img = sensor.snapshot().compress(quality=50)
			base64 = ubinascii.b2a_base64(img)
			MQTT.publish("86Box/Photo", base64)
			MQTT.connect()
			del img
			del base64
		if msg == b'update':
			print("Check update")
			print(ota_updater.check_for_update_to_install_during_next_reboot())
			print("Reset")
			machine.reset()
			print("Not supposed to show")
	MQTT.set_callback(callback)
	MQTT.subscribe(mainTopic + "/command")
	MQTT.publish(mainTopic, "OpenMV ONLINE!")
	def sendMQTT(subTopic, msg):
		subTopic = mainTopic + "/" + subTopic
		MQTT.publish(subTopic, msg)
	def sendLINE(msg):
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
		print("Waiting")
		MQTT.wait_msg()
		time.sleep_ms(1000)
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
def boot():
	download_and_install_update_if_available()
	start()
boot()