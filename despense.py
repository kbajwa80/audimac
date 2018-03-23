#! /usr/bin/python
#Kanwar Bajwa: March 21,2018
#This script is a test script for MCP23017 and using address 0x20 only

import smbus
import time 
import atexit 
import sys

#-----Pi Bus Address-----#
bus = smbus.SMBus(1) #define bus address(for rev its 1)

#-----Drawer address assignement-----#
chip_addr = [0x20,0x21,0x22,0x23,0x24,0x25,0x26] #I2C address of different chips (Each drawer has its own i2c address)

#Drawer addresses
drawer = [chip_addr[0],
	chip_addr[1],
	chip_addr[2],
	chip_addr[3],
	chip_addr[4],
	chip_addr[5],
	chip_addr[6]]

#-----Componenet address assignment-----#
Bank = [0x12,0x13,0x14,0x15,0x16] #PCA9698DGG has 5 banks with 8 I/O each
GPIO = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80]

#Motor addresses
motor = [[Bank[0],GPIO[0]],
	[Bank[0],GPIO[1]],
	[Bank[0],GPIO[2]],
	[Bank[0],GPIO[3]],
	[Bank[0],GPIO[4]],
	[Bank[0],GPIO[5]],
	[Bank[0],GPIO[6]],
	[Bank[0],GPIO[7]],
	[Bank[1],GPIO[0]],
	[Bank[1],GPIO[1]],
	[Bank[1],GPIO[2]],
	[Bank[1],GPIO[3]]]

#TOF reset address
tof_s = [[Bank[1],GPIO[4]],
        [Bank[1],GPIO[5]],
        [Bank[1],GPIO[6]],
        [Bank[1],GPIO[7]],
        [Bank[2],GPIO[0]],
        [Bank[2],GPIO[1]],
        [Bank[2],GPIO[2]],
        [Bank[2],GPIO[3]],
	[Bank[2],GPIO[4]],
        [Bank[2],GPIO[5]],
        [Bank[2],GPIO[6]],
        [Bank[2],GPIO[7]]]

#End of silo address
eos_s = [[Bank[2],GPIO[0]],
        [Bank[2],GPIO[1]],
        [Bank[2],GPIO[2]],
        [Bank[2],GPIO[3]],
        [Bank[2],GPIO[4]],
        [Bank[2],GPIO[5]],
        [Bank[2],GPIO[6]],
        [Bank[2],GPIO[7]],
        [Bank[3],GPIO[0]],
        [Bank[3],GPIO[1]],
        [Bank[3],GPIO[2]],
#        [Bank[3],GPIO[3]]]
	[Bank[1],GPIO[7]]]

#beam Sensor
#beam_s = [Bank[3],GPIO[3]]
beam_s = [Bank[1],GPIO[6]]


#####-----set Bank for input and  output-----##### 
#for addr in (drawer):
for addr in ([drawer[0]]): # remove after testing
	bus.write_byte_data(addr,0x00,0x00) # Set all of BankA pins to output
#	bus.write_byte_data(addr,0x01,0x00) # Set all of BankB pins to output
#	bus.write_byte_data(addr,0x01,beam_s[1]) #For Testing, remove later, input pin for beam testing 
	bus.write_byte_data(addr,0x01,0xC0) #For Testing, remove later, input pin for beam testing 
	bus.write_byte_data(addr,0x02,0X00) # Set all of BankC pins to output
        bus.write_byte_data(addr,0x03,0XFF) # Set all of BankD pins to Input
	bus.write_byte_data(addr,0x04,0XFF) # Set all of BankE pins to Input

#####-----Motor Operation-----#####
#Status of The  Motor
def motor_status(drawerID,motorID):
        return (bus.read_byte_data(drawer[drawerID],motor[motorID][0]))

#Run Motor 
def run_motor(drawerID,motorID):
	if (motor_status(drawerID,motorID) & motor[motorID][1]):
		print "Active motor detected:Exiting"	
	else:
		print "Activating Motor"
		bus.write_byte_data(drawer[drawerID],motor[motorID][0],motor[motorID][1])

#Stop Motor
def stop_motor(drawerID,motorID):
        bus.write_byte_data(drawer[drawerID],motor[motorID][0],0x00)
	print "Stopping Motor"

#Status of beam Sensor  
def beam_status(drawerID):
	return (bus.read_byte_data(drawer[drawerID],beam_s[0]) & beam_s[1])

#Status of end of silo Sensor
def silo_status(drawerID,motorID):
        return (bus.read_byte_data(drawer[drawerID],eos_s[siloID][0]) & eos_s[siloID][1])
	
####----Main logic-----#####
drawerID=0
motorID=11
siloID=motorID

while True:
	try:
		if (beam_status(drawerID) == 0) or (silo_status(drawerID,siloID) == 0):
			stop_motor(drawerID,motorID)
			break
		else:
			run_motor(drawerID,motorID)
	except (KeyboardInterrupt):
		print "Exiting"
		break

