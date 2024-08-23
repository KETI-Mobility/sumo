##############################################################################
# File: Message_BSMplus.py
#
# Description: Basic Safety Message (BSM) + Perception Information Message (PIM) class
# Broadcasted by vehicles to inform other vehicles about their status
# 주변에 인식된 객체 등의 정보를 BSM 메시지에 추가하여 전송하는 안전메시지
#
##############################################################################

import os
import sys
import traci
import math
from enum import Enum
from Message import Message


class BSMplus(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_BSMplus, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		

	def show_msg(self):
		print("[BSM+] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))
