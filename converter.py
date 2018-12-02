import smbus
import time

class ADCREADDATA:
    lastRawDataA0 = 0
    lastConverValueA0 = 0.0
    lastRawDataA1 = 0
    lastConverValueA1 = 0.0
    lastRawDataA2 = 0
    lastConverValueA2 = 0.0
    lastRawDataA3 = 0
    lastConverValueA3 = 0.0

'''
	FILE FOR PCF8591 8 BIT, 4 CHANNELS ADC
'''
class ADCCHANNELS:
	devAddress = 0x48
	A0 = 0x00
	A1 = 0x01
	A2 = 0x02
	A3 = 0x03
	RESOLUTION = 255
	VOLTAGE = 3.3

'''
	CLASS RESPONSIBLE FOR GETTING DATA FROM I2C
'''
class AdcValue(object):
	lastRawData = 0
	lastConvertValue = 0.0
	i2cBus = smbus.SMBus(1)

	def empty_read():
		AdcValue.i2cBus.write_byte(ADCCHANNELS.devAddress, 0x00)
		time.sleep(400/1000000)
		return readValue

	def getRawData(channel):
		AdcValue.i2cBus.write_byte(ADCCHANNELS.devAddress, channel)
		time.sleep(400/1000000)
		readValue = AdcValue.i2cBus.read_byte(ADCCHANNELS.devAddress)
		return readValue

	def getRawValueFromChannel0():
		rawDataA0 = AdcValue.getRawData(ADCCHANNELS.A0)
		ADCREADDATA.lastRawDataA0 = rawDataA0;
		return rawDataA0

	def getRawValueFromChannel1():
		rawDataA1 = AdcValue.getRawData(ADCCHANNELS.A1)
		ADCREADDATA.lastRawDataA1 = rawDataA1;
		return rawDataA1

	def getRawValueFromChannel2():
		rawDataA2 = AdcValue.getRawData(ADCCHANNELS.A2)
		ADCREADDATA.lastRawDataA2 = rawDataA2;
		return rawDataA2

	def getRawValueFromChannel3():
		rawDataA3 = AdcValue.getRawData(ADCCHANNELS.A3)
		ADCREADDATA.lastRawDataA3 = rawDataA3;
		return rawDataA3

	def getRawDataFrom(channel):
		if channel == 0:
			convertValue = AdcValue.getRawValueFromChannel0()
		if channel == 1:
			convertValue = AdcValue.getRawValueFromChannel1()
		if channel == 2:
			convertValue = AdcValue.getRawValueFromChannel2()
		if channel == 3:
			convertValue = AdcValue.getRawValueFromChannel3()

		return convertValue;

	def convertValueCalcul(rawData, adcRefVoltage, adcResolution):
		convertValueRet = (rawData * adcRefVoltage / adcResolution)
		AdcValue.lastConvertValue = convertValueRet
		return convertValueRet

	def convertValueChannel(channel):
		if channel == 0:
			ADCREADDATA.lastConverValueA0 = AdcValue.convertValueCalcul(ADCREADDATA.lastRawDataA0,
																		ADCCHANNELS.VOLTAGE,
																		ADCCHANNELS.RESOLUTION)
		if channel == 1:
			ADCREADDATA.lastConverValueA1 = AdcValue.convertValueCalcul(ADCREADDATA.lastRawDataA1,
																			 ADCCHANNELS.VOLTAGE,
																			 ADCCHANNELS.RESOLUTION)
		if channel == 2:
			ADCREADDATA.lastConverValueA2 = AdcValue.convertValueCalcul(ADCREADDATA.lastRawDataA2,
																			 ADCCHANNELS.VOLTAGE,
																			 ADCCHANNELS.RESOLUTION)
		if channel == 3:
			ADCREADDATA.lastConverValueA3 = AdcValue.convertValueCalcul(ADCREADDATA.lastRawDataA3,
																			 ADCCHANNELS.VOLTAGE,
																			 ADCCHANNELS.RESOLUTION)
                                                                             
	def readConvertValueChannel(channel):
		AdcValue.getRawDataFrom(channel)
		AdcValue.convertValueChannel(channel)
		print("CH%d:%1.3f" % ( channel, AdcValue.lastConvertValue) )

# channel 0 fotorezystor
# channel 1 termistor
# channel 2 MQ 3?
# channel 3 MQ-135+

if __name__ == "__main__":
	while 1:
		AdcValue.empty_read
		AdcValue.readConvertValueChannel(0)
		time.sleep(400/1000000)
		AdcValue.readConvertValueChannel(1)
		time.sleep(400/1000000)
		AdcValue.readConvertValueChannel(2)
		time.sleep(400/1000000)
		AdcValue.readConvertValueChannel(3)
		print("\r\n")
		time.sleep(2)
