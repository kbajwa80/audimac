#!/bin/usr/python
# Usage: get_range_multi_sensor.py <sensor Number>
# Kanwar Bajwa

import argparse
import smbus
import struct
import time
import sys
import RPi.GPIO as GPIO
import os
from sys import argv
import RPi.GPIO as GPIO

##### Unmask distance 
def makeuint16(lsb, msb):
    return ((msb & 0xFF) << 8)  | (lsb & 0xFF)

##### Address Assignment 
bus = smbus.SMBus(1)		# pi bus	
address = 0x29			# Defult VL53L0X address 
sensors = [40,38]		# GPIO for Sensor
snum = (int(argv[(1)]) -1)	# Sensor to Activate

##### GPIO Setup for xreset 
GPIO.setmode(GPIO.BOARD)			# GPIO scheme

def reset_sensor():
	for i in sensors:
		GPIO.setup(sensors, GPIO.OUT) 		# Setup GPIO for shutdown pins on each VL53L0X
		GPIO.output(sensors, GPIO.LOW)
		time.sleep(.1)

def set_sensor(snum):
	GPIO.output(sensors[snum], GPIO.HIGH)		# Set required pin to high VL53L0X
	time.sleep(.1)

reset_sensor()		# Reseting all/any Sensor 
set_sensor(snum)	# Setting up Required Sensor

##### For Reference
VL53L0X_REG_IDENTIFICATION_MODEL_ID		= 0x00c0
VL53L0X_REG_IDENTIFICATION_REVISION_ID		= 0x00c2
VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD	= 0x0050
VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD	= 0x0070
VL53L0X_REG_SYSRANGE_START			= 0x000
VL53L0X_REG_RESULT_INTERRUPT_STATUS 		= 0x0013
VL53L0X_REG_RESULT_RANGE_STATUS 		= 0x0014

##### Initialze the device
bus.write_byte_data(address, VL53L0X_REG_SYSRANGE_START, 0x01)

##### Status of the device
cnt = 0
while (cnt < 100): # 1 second waiting time max
	time.sleep(.1)
	val = bus.read_byte_data(address, VL53L0X_REG_RESULT_RANGE_STATUS)
	if (val & 0x01):
		break
	cnt += 1

if (val & 0x01):
	print "Device is ready"
else:
	print "Device is not ready"
	GPIO.cleanup()  # Cleaning up GPIO Channels
	sys.exit() 

##### Get one reading by taking average
Av_distance = 0
i = 0;s = 0
while (i < 100):
	try:
		bus.write_byte_data(address, 0x00, 0x01)
		data = bus.read_i2c_block_data(address, 0x14, 16)
		SensorStatus = ((data[0] & 0x78) >> 3)
		if SensorStatus == 11:
			i += 1
			Av_distance += makeuint16(data[11],data[10])
		else:
			s += 1
		if s > 10000:
			raise SystemExit	
	except (SystemExit):
		GPIO.cleanup()  # Cleaning up GPIO Channels
		print "Out of Range: Error"
		sys.exit()
print Av_distance/i


reset_sensor()	# Reseting Sensor
GPIO.cleanup()	# Cleaning up GPIO Channels
