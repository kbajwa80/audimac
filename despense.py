#! /usr/bin/python
#Kanwar Bajwa: March 21,2018

import smbus
import time 
import atexit 
import sys
from sys import argv

#-----Pi Bus Address-----#
bus = smbus.SMBus(1) #define bus address(for rev its 1)

#-----Chip address assignement-----#
#Drawers
chip_addr = [0x20,0x21,0x22,0x23,0x24,0x25,0x26] #I2C address of different chips (Each drawer has its own i2c address)

#Time of flight sensor
tof_addr  = 0x29				 # Defult VL53L0X address 

#Drawer addresses
drawer = [chip_addr[0],
	chip_addr[1],
	chip_addr[2],
	chip_addr[3],
	chip_addr[4],
	chip_addr[5],
	chip_addr[6]]

#-----Componenet address assignment-----#
r_addr     = [0x00,0x01,0x02,0x03,0x04] 						#Input Port registers (address 00h to 04h) 
conf_addr  = [0x18,0x19,0x1A,0x1B,0x1C]							#I/O Configuration registers
rw_addr    = [0x88,0x89,0x8A,0x8B,0x8C] 						#RW Command
Bank       = [rw_addr[0],rw_addr[1],rw_addr[2],r_addr[3],r_addr[4]]
GPIO 	   = [0xFE,0xFD,0xFB,0xF7,0xEF,0xDF,0xBF,0x7F,0x0E,0x0D,0x0B,0x07]
RGPIO 	   = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1F,0x2F,0x4F,0x8F]

#Motor addresses
motor = [[Bank[0],GPIO[0],RGPIO[0]],
	[Bank[0],GPIO[1],RGPIO[1]],
	[Bank[0],GPIO[2],RGPIO[2]],
	[Bank[0],GPIO[3],RGPIO[3]],
	[Bank[0],GPIO[4],RGPIO[4]],
	[Bank[0],GPIO[5],RGPIO[5]],
	[Bank[0],GPIO[6],RGPIO[6]],
	[Bank[0],GPIO[7],RGPIO[7]],
	[Bank[1],GPIO[8],RGPIO[0]],
	[Bank[1],GPIO[9],RGPIO[1]],
	[Bank[1],GPIO[10],RGPIO[2]],
	[Bank[1],GPIO[11],RGPIO[3]]]

#TOF reset address
tof_s = [[Bank[1],RGPIO[8]],
        [Bank[1],RGPIO[9]],
        [Bank[1],RGPIO[10]],
        [Bank[1],RGPIO[11]],
        [Bank[2],RGPIO[0]],
        [Bank[2],RGPIO[1]],
        [Bank[2],RGPIO[2]],
        [Bank[2],RGPIO[3]],
	[Bank[2],RGPIO[4]],
        [Bank[2],RGPIO[5]],
        [Bank[2],RGPIO[6]],
        [Bank[2],RGPIO[7]]]

#End of silo address
eos_s = [[Bank[4],RGPIO[7]],
        [Bank[4],RGPIO[6]],
        [Bank[4],RGPIO[5]],
        [Bank[4],RGPIO[4]],
        [Bank[4],RGPIO[3]],
        [Bank[4],RGPIO[2]],
        [Bank[4],RGPIO[1]],
        [Bank[4],RGPIO[0]],
        [Bank[3],RGPIO[7]],
        [Bank[3],RGPIO[6]],
        [Bank[3],RGPIO[5]],
        [Bank[3],RGPIO[4]]]

#beam Sensor
beam_s = [Bank[3],RGPIO[3]]

#####-----For Testing-----#####
drawerID=0
motorID=(int(argv[(1)]) -1)	# Sensor to Activate
siloID=motorID
tofID=motorID
###############################

#####-----set Bank for input and  output-----##### 
#for addr in (drawer):
for addr in ([drawer[0]]): # remove after testing
	bus.write_byte_data(addr,conf_addr[0],0x00) 
	bus.write_byte_data(addr,conf_addr[1],0x00)
	bus.write_byte_data(addr,conf_addr[2],0x00)
	bus.write_byte_data(addr,conf_addr[3],0xFF) 
	bus.write_byte_data(addr,conf_addr[4],0xFF)

#####-----Sensor Operation(input)-----#####

# Unmask distance 
def makeuint16(lsb, msb):
    return ((msb & 0xFF) << 8)  | (lsb & 0xFF)

#Status of beam Sensor
def beam_status(drawerID):
        return (bus.read_byte_data(drawer[drawerID],beam_s[0]) & beam_s[1])

#Status of end of silo Sensor
def silo_status(drawerID,siloID):
        return (bus.read_byte_data(drawer[drawerID],eos_s[siloID][0]) & eos_s[siloID][1])

#####-----tof Operation-----#####
#Setup for xreset
def reset_tof():
        for tof in (tof_s):
                if tof[0] == Bank[1]:
                        bus.write_byte_data(drawer[drawerID],tof[0],0x0F)
                else:
                        bus.write_byte_data(drawer[drawerID],tof[0],0x00)

def xshut_tof(tofID):
        bus.write_byte_data(drawer[drawerID],tof_s[tofID][0],tof_s[tofID][1])
        time.sleep(.1)



reset_tof()
xshut_tof(tofID)



#####-----Motor Operation-----#####

#Status of The  Motor
def motor_status(drawerID,motorID):
        return (bus.read_byte_data(drawer[drawerID],motor[motorID][0]))

#Run Motor 
def run_motor(drawerID,motorID):
	if (~motor_status(drawerID,motorID) & motor[motorID][2]):
		#print (motor_status(drawerID,motorID) & motor[motorID][1])
		#print "Active motor detected:Exiting"	
		pass
	else:
	        print "Activating motor"
		#print (~motor_status(drawerID,motorID) & motor[motorID][1])
		bus.write_byte_data(drawer[drawerID],motor[motorID][0],motor[motorID][1])

#Stop Motor
def stop_motor(drawerID,motorID):
	if motor[motorID][0] == Bank[0]:
        	bus.write_byte_data(drawer[drawerID],motor[motorID][0],0xFF)
		print "Stopping Motor"
	else:
		bus.write_byte_data(drawer[drawerID],motor[motorID][0],0x0F)
		print "Stopping Motor"

#####----Main despense logic-----#####

while True:
	try:
		if (beam_status(drawerID) == 0) and (silo_status(drawerID,siloID) == 0):
			run_motor(drawerID,motorID)
		else:
			stop_motor(drawerID,motorID)
			break
	except (KeyboardInterrupt):
		print "Exiting"
		break

#####----Main Inventory Count logic-----#####

# For Reference
VL53L0X_REG_IDENTIFICATION_MODEL_ID		= 0x00c0
VL53L0X_REG_IDENTIFICATION_REVISION_ID		= 0x00c2
VL53L0X_REG_PRE_RANGE_CONFIG_VCSEL_PERIOD	= 0x0050
VL53L0X_REG_FINAL_RANGE_CONFIG_VCSEL_PERIOD	= 0x0070
VL53L0X_REG_SYSRANGE_START			= 0x000
VL53L0X_REG_RESULT_INTERRUPT_STATUS 		= 0x0013
VL53L0X_REG_RESULT_RANGE_STATUS 		= 0x0014

# Initialze the device
bus.write_byte_data(tof_addr, VL53L0X_REG_SYSRANGE_START, 0x01)

# Status of the device
cnt = 0
while (cnt < 100): # 1 second waiting time max
	time.sleep(.1)
	val = bus.read_byte_data(tof_addr, VL53L0X_REG_RESULT_RANGE_STATUS)
	if (val & 0x01):
		break
	cnt += 1

if (val & 0x01):
	#print "Device is ready"
	pass
else:
	print "Device is not ready"
	sys.exit() 

# Get one reading by taking average
Av_distance = 0
i = 0;s = 0
while (i < 100):
	try:
		bus.write_byte_data(tof_addr, 0x00, 0x01)
		data = bus.read_i2c_block_data(tof_addr, 0x14, 16)
		SensorStatus = ((data[0] & 0x78) >> 3)
		if SensorStatus == 11:
			i += 1
			Av_distance += makeuint16(data[11],data[10])
		else:
			s += 1
		if s > 10000:
			raise SystemExit	
	except (SystemExit):
		print "Out of Range: Error"
		sys.exit()
print "Remaining items ",Av_distance/i
reset_tof()
