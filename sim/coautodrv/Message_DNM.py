##############################################################################
# File: Message_DNM.py
#
# Description: Driving Negotiation Message (DNM) class
# Transmitted by a vehicle to negotiate the order of entry to the intersection
# 필요한 주행협상 정보를 생성하여 상대방 차량에 진입 순서를 요청(Req)하고 응답(Rep)하는 안전메시지
#
##############################################################################

import os
import sys
import traci
import math
from enum import Enum
from Message import Message


class DNMReq(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DNMREQ, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id


	def show_msg(self):
		print("[DNM Req] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


class DNMResp(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DNMRESP, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id


	def show_msg(self):
		print("[DNM Res] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))
