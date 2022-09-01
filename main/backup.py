import time, pyb
led = pyb.LED(3)
usb = pyb.USB_VCP()
while(not usb.isconnected()):
	led.on()
	time.sleep_ms(150)
	led.off()
	time.sleep_ms(100)
	led.on()
	time.sleep_ms(150)
	led.off()
	time.sleep_ms(600)
led = pyb.LED(2)
while(usb.isconnected()):
	led.on()
	time.sleep_ms(150)
	led.off()
	time.sleep_ms(100)
	led.on()
	time.sleep_ms(150)
	led.off()
	time.sleep_ms(600)