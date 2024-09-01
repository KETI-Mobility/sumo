##############################################################################
# File: Message.py
#
# Description: Message class
# Transmitted by a vehicle 
#
##############################################################################

import os
import sys
import math
from enum import Enum
from typing import TYPE_CHECKING
import GlobalSim

if TYPE_CHECKING:
	from Vehicle import Vehicle, T_CDA, E_CDA, C_VEH, CE_VEH, N_VEH, Maneuver
	from Channel import Channel


class Message:
	
	class Type(Enum):
		MSG_NONE	= 0
		MSG_BSM     = 1
		MSG_BSMplus = 2
		MSG_DMM     = 3
		MSG_DNMREQ  = 4
		MSG_DNMRESP = 5
		MSG_EDM	 	= 6
	
	def __init__(self, msg_type, sender_vehicle_id, sender_vehicle_type):
		
		GlobalSim.msg_id += 1
		self.msg_id					= GlobalSim.msg_id
		
		self.msg_type				= msg_type
		self.sender_vehicle_id		= sender_vehicle_id
		self.sender_vehicle_type	= sender_vehicle_type

	def show_msg(self) -> None:
		pass
		# print("Step({}) [Message] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type))


##############################################################################
# Basic Safety Message (BSM) class
# 
# Broadcasted by vehicles to inform other vehicles about their status
# SAE J2735 표준 문서에 정리된 메시지 셋으로 차량의 속도, 방향, 위치 등을 주기적으로 방송하는 안전메시지
#
##############################################################################

class BSM(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed):
		super().__init__(Message.Type.MSG_BSM, sender_vehicle_id, sender_vehicle_type)
		self.sender_location	= sender_location
		self.sender_speed		= sender_speed

	def show_msg(self) -> None:
		pass
		# print("Step({}) [BSM] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed))


##############################################################################
# Emergency Driving Message (EDM) class
#
#  Broadcasted by vehicles to inform other vehicles about their status
# 긴급차량의 주행의도를 알려주어 주변 차량들의 주행협조를 요청하는 안전메시지
#
##############################################################################

class EDM(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed):
		super().__init__(Message.Type.MSG_BSMplus, sender_vehicle_id, sender_vehicle_type)
		self.sender_location = sender_location
		self.sender_speed = sender_speed

	def show_msg(self) -> None:
		pass
		# print("Step({}) [EDM] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed))


##############################################################################
# Basic Safety Message (BSM) + Perception Information Message (PIM) class
#
# Broadcasted by vehicles to inform other vehicles about their status
# 주변에 인식된 객체 등의 정보를 BSM 메시지에 추가하여 전송하는 안전메시지
#
##############################################################################

class BSMplus(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_BSMplus, sender_vehicle_id, sender_vehicle_type)
		self.sender_location = sender_location
		self.sender_speed = sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id
		
	def show_msg(self) -> None:
		pass
		# print("Step({}) [BSM+] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id))


##############################################################################
# Driving Maneuver Message (DMM) class
#
#  Broadcasted by vehicles to inform other vehicles about their status
# 교차로 등에서 차량의 주행의도를 주변에 알려주는 안전메시지
#
##############################################################################

class DMM(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DMM, sender_vehicle_id, sender_vehicle_type)
		self.sender_location = sender_location
		self.sender_speed = sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id

		self.maneuver 			= Maneuver.NONE

	def show_msg(self) -> None:
		pass
		# print("Step({}) [DMM] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}, Maneuver: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id, self.maneuver))


##############################################################################
# Driving Negotiation Message (DNM) class
#
#  Transmitted by a vehicle to negotiate the order of entry to the intersection
# 필요한 주행협상 정보를 생성하여 상대방 차량에 진입 순서를 요청(Req)하고 응답(Rep)하는 안전메시지
#
##############################################################################

class DNMReq(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DNMREQ, sender_vehicle_id, sender_vehicle_type)
		self.sender_location = sender_location
		self.sender_speed = sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id

	def show_msg(self) -> None:
		pass
		# print("Step({}) [DNMReq] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}, Maneuver: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id, self.maneuver))


class DNMResp(Message):

	def __init__(self, sender_vehicle_id, sender_vehicle_type, sender_location, sender_speed, sender_acceleration, sender_heading, sender_lane_id):
		super().__init__(Message.Type.MSG_DNMRESP, sender_vehicle_id, sender_vehicle_type)
		self.sender_location = sender_location
		self.sender_speed = sender_speed
		self.sender_acceleration= sender_acceleration
		self.sender_heading		= sender_heading
		self.sender_lane_id		= sender_lane_id

	def show_msg(self) -> None:
		pass
		# print("Step({}) [DNMResp] Msg ID: {}, Type: {} from Sender ID: {}, Sender Vehicle Type: {}, ({}, {}), Speed: {}, Accel: {}, Heading: {}, Lane: {}, Maneuver: {}".format(GlobalSim.step, self.msg_id, self.msg_type, self.sender_vehicle_id, self.sender_vehicle_type, self.sender_location[0], self.sender_location[1], self.sender_speed, self.sender_acceleration, self.sender_heading, self.sender_lane_id, self.maneuver))

