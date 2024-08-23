##############################################################################
# File: Message_DMM.py
#
# Description: Driving Maneuver Message (DMM) class
# Broadcasted by vehicles to inform other vehicles about their status
# 교차로 등에서 차량의 주행의도를 주변에 알려주는 안전메시지
#
##############################################################################

import os
import sys
import traci
import math
from enum import Enum
from Message import Message

class Maneuver(Enum):
		NONE	= 0
		GO		= 1
		YIELD	= 2

class DMM(Message):
	
	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DMM, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id

		self.maneuver 			= Maneuver.NONE

	def show_msg(self):
		print("[DMM] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))
