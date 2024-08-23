##############################################################################
# File: Message.py
#
# Description: Message class
# Transmitted by a vehicle 
#
##############################################################################

import os
import sys
import traci
import math
from enum import Enum

# Global variable to accumulate a number to use as an ID
global_msg_id = 0

class Message:
	
	class Type(Enum):
		MSG_NONE	= 0
		MSG_BSM     = 1
		MSG_BSMplus = 2
		MSG_DMM     = 3
		MSG_DNMREQ  = 4
		MSG_DNMRESP = 5
	
	def __init__(self, msg_type, timestamp, sender_vehicle_id, sender_vehicle_type):
		global_msg_id += 1
		self.msg_id					= global_msg_id
		
		self.msg_type				= msg_type
		self.sender_vehicle_id		= sender_vehicle_id
		self.sender_vehicle_type	= sender_vehicle_type

	def show_msg(self):
		print("Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}".format(self.sender_vehicle_id, self.sender_vehicle_type))
