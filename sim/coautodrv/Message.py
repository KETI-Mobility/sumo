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
from Vehicle import *
from Channel import *


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
		MSG_EDM	 	= 6
	
	def __init__(self, msg_type, timestamp, sender_vehicle_id, sender_vehicle_type):
		global_msg_id += 1
		self.msg_id					= global_msg_id
		
		self.msg_type				= msg_type
		self.sender_vehicle_id		= sender_vehicle_id
		self.sender_vehicle_type	= sender_vehicle_type

	def show_msg(self) -> None:
		print("Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}".format(self.sender_vehicle_id, self.sender_vehicle_type))


##############################################################################
# Basic Safety Message (BSM) class
# 
# Broadcasted by vehicles to inform other vehicles about their status
# SAE J2735 표준 문서에 정리된 메시지 셋으로 차량의 속도, 방향, 위치 등을 주기적으로 방송하는 안전메시지
#
##############################################################################

class BSM(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_BSM, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		

	def show_msg(self) -> None:
		print("[BSM] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


##############################################################################
# Basic Safety Message (BSM) + Perception Information Message (PIM) class
#
# Broadcasted by vehicles to inform other vehicles about their status
# 주변에 인식된 객체 등의 정보를 BSM 메시지에 추가하여 전송하는 안전메시지
#
##############################################################################

class BSMplus(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_BSMplus, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		

	def show_msg(self) -> None:
		print("[BSM+] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


##############################################################################
# Driving Maneuver Message (DMM) class
#
#  Broadcasted by vehicles to inform other vehicles about their status
# 교차로 등에서 차량의 주행의도를 주변에 알려주는 안전메시지
#
##############################################################################

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

	def show_msg(self) -> None:
		print("[DMM] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


##############################################################################
# Emergency Driving Message (EDM) class
#
#  Broadcasted by vehicles to inform other vehicles about their status
# 긴급차량의 주행의도를 알려주어 주변 차량들의 주행협조를 요청하는 안전메시지
#
##############################################################################

class EDM(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_EDM, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		

	def show_msg(self) -> None:
		print("[BSM] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


##############################################################################
# Driving Negotiation Message (DNM) class
#
#  Transmitted by a vehicle to negotiate the order of entry to the intersection
# 필요한 주행협상 정보를 생성하여 상대방 차량에 진입 순서를 요청(Req)하고 응답(Rep)하는 안전메시지
#
##############################################################################

class DNMReq(Message):

	def __init__(self, timestamp, sender_vehicle_id, sender_vehicle_type, sender_x_location, sender_y_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DNMREQ, timestamp, sender_vehicle_id, sender_vehicle_type)
		self.sender_x_location	= sender_x_location
		self.sender_y_location	= sender_y_location
		self.sender_speed		= sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id


	def show_msg(self) -> None:
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


	def show_msg(self) -> None:
		print("[DNM Res] Msg ID: {}, Type: {}, Time: {}".format(self.msg_id, self.msg_type, self.timestamp))
		print("  + Sender: ID: {}, Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(self.sender_vehicle_id, self.sender_vehicle_type, self.sender_x_location, self.sender_y_location, self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))

