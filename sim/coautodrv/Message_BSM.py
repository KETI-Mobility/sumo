##############################################################################
# File: Message_BSM.py
#
# Description: Basic Safety Message (BSM) class
# Broadcasted by vehicles to inform other vehicles about their status
# SAE J2735 표준 문서에 정리된 메시지 셋으로 차량의 속도, 방향, 위치 등을 주기적으로 방송하는 안전메시지
#
##############################################################################

import os
import sys
import traci
import math
from enum import Enum
from Message import Message


class BSM(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_BSM, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		

	def show_msg(self):
		print("[BSM] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))
