#!/usr/bin/env python
import PCF8591 as ADC
import time

def setup():
	ADC.setup(0x48)

def loop():
	while True:
		print ADC.read(0) * 3.3 / 255
		print ADC.read(1) * 3.3 / 255
		print ADC.read(2) * 3.3 / 255
		print ADC.read(3) * 3.3 / 255
		print "/r/n"
		time.sleep(1)

def destroy():
	ADC.write(0)

# channel 0 fotorezystor
# channel 1 termistor
# channel 2 MQ 3?
# channel 3 MQ-135+

if __name__ == "__main__":
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()
