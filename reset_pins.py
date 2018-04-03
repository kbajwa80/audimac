#! /usr/bin/python
#Kanwar Bajwa: March 21,2018
#This script is a test script for MCP23017 and using address 0x20 only

import smbus
import time 
import atexit 
import sys

#-----Pi Bus Address-----#
bus = smbus.SMBus(1) #define bus address(for rev its 1)

#-----Declare pins as output-----#
for bank in range(24,29): # remove after testing
	try:
        	print bus.read_byte_data(0x20,bank)
		bus.write_byte_data(0x20,bank,0x00) # Set all of BankA pins to output
		print bus.read_byte_data(0x20,0x00)
	except:
		print "error",bank

#-----Set Output pin-----#
for bank in range(136,141): # remove after testing
        try:
                bus.write_byte_data(0x20,bank,0xFF) # Set all of BankA pins to output
                print bus.read_byte_data(0x20,bank)
        except:
                print "error",bank

#-----reading state of pins-----#
for bank in range(0x00,0x05): # remove after testing
        try:
                print bus.read_byte_data(0x20,bank),bank
        except:
                print "error",bank
