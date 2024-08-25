import os
import sys
import traci
import math
from enum import Enum
from Message import *
from Channel import *


class Maneuver(Enum):
		NONE				= 0
		GO_STRAIGHT			= 1
		TURN_LEFT			= 2
		TURN_RIGHT			= 3
		LANECHANGE_LEFT		= 4
		LANECHANGE_RIGHT	= 5
		U_TURN				= 6
		YIELD				= 7
		STOP				= 8
		PARK				= 9
		EMERGENCY_STOP		= 10

class Vehicle:
	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		self.vehicle_id = vehicle_id
		self.vehicle_type = vehicle_type
		self.vehicle_color = vehicle_color
		self.vehicle_length = vehicle_length
		self.vehicle_width = vehicle_width
		self.cur_location = (0,0)	# Initial location of the vehicle
		self.x_location = x_location	# Location of the roundabout
		self.distance = self.get_distance()

	def update_location(self, new_location) -> None:
		self.cur_location = new_location

	def get_distance(self) -> float:
		self.distance = math.sqrt((self.x_location[0] - self.cur_location[0])**2 + (self.x_location[1] - self.cur_location[1])**2)
		return self.distance
	
	def show_info(self) -> None:
		print("Vehicle ID: {}, Type: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.distance))


##############################################################################
# Normal Vehicle (N-VEH) class
#
# Normal Vehicle, 통신기능 없이 일반 운전자가 주행하는 일반차량
# 전송가능 메시지: 없음
#
##############################################################################

class N_VEH(Vehicle):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		super().__init__(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location)
		self.state = N_VEH.State.INITIAL

	def update_location(self, new_location) -> None:
		super().update_location(new_location)
		self.update_state()

	def get_location(self) -> tuple:
		return (self.x_location, self.y_location)

	def show_info(self) -> None:
		print("[N-VEH] Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))



##############################################################################
# Connected Vehicle (C-VEH) class
#
#  기본적인 안전 메시지를 송수신하며 일반 운전자가 주행하는 차량 
# 전송가능 메시지: BSM
# (제약사항) 수십 cm이하의 위치정보 제공이 요구됨
#
##############################################################################

class C_VEH(Vehicle):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		super().__init__(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location)
		self.state = C_VEH.State.INITIAL

	def update_location(self, new_location) -> None:
		super().update_location(new_location)
		self.update_state()

	def get_location(self) -> tuple:
		return (self.x_location, self.y_location)
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.get_location())
		return bsm

	def send_bsm(self, channel:Channel) -> None:
		print("BSM sent")
		channel.append(self.create_bsm())

	def receive_bsm(self, bsm:BSM) -> None:
		print("BSM received")
		# TODO: process bsm


	def update_state(self) -> None:
		if self.state == C_VEH.State.INITIAL:
			print("INITIAL -> ADDED")
			self.state = C_VEH.State.ADDED
		elif self.state == C_VEH.State.ADDED and self.get_distance(self) < 100:
			print("ADDED -> APPROACHING")
			self.state = C_VEH.State.APPROACHING
		elif self.state == C_VEH.State.APPROACHING and self.get_distance(self) < 50:
			print("APPROACHING -> INSIDE")
			self.state = C_VEH.State.INSIDE
		elif self.state == C_VEH.State.INSIDE and self.get_distance(self) > 50:
			print("INSIDE -> EXITING")
			self.state = C_VEH.State.EXITING
		elif self.state == C_VEH.State.EXITING and self.get_distance(self) > 100:
			print("EXITING -> REMOVED")
			self.state = C_VEH.State.REMOVED

	def show_info(self) -> None:
		print("[C-VEH] Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))


##############################################################################
#  Connected Emergency Vehicle (CE-VEH) class
# 
# 전송가능 메시지: BSM, EDM
# 주변 차량에게 강제적으로 경로변경 요청을 명령할 수 있는 차량
#
##############################################################################

class CE_VEH(Vehicle):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		super().__init__(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location)
		self.state = CE_VEH.State.INITIAL

	def update_location(self, new_location) -> None:
		super().update_location(new_location)
		self.update_state()

	def create_bsm(self) -> BSMplus:
		bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.get_location())
		return bsm_plus
	
	def create_edm(self) -> EDM:
		edm = EDM(self.vehicle_id, self.vehicle_type, self.get_location())
		return edm
	
	def send_bsm(self, channel:Channel) -> None:
		print("BSM+ sent")
		channel.append(self.create_bsm_plus())

	def send_edm(self, channel:Channel) -> None:
		print("EDM sent")
		channel.append(self.create_edm())

	def receive_bsm(self, bsm_plus:BSMplus) -> None:
		print("BSM_ received")
		# TODO: process bsm+

	def receive_edm(self, edm:EDM) -> None:
		print("EDM received")
		# TODO: process edm


	def update_state(self) -> None:
		if self.state == CE_VEH.State.INITIAL:
			print("INITIAL -> ADDED")
			self.state = CE_VEH.State.ADDED
		elif self.state == CE_VEH.State.ADDED and self.get_distance(self) < 100:
			print("ADDED -> APPROACHING")
			self.state = CE_VEH.State.APPROACHING
		elif self.state == CE_VEH.State.APPROACHING and self.get_distance(self) < 50:
			print("APPROACHING -> INSIDE")
			self.state = CE_VEH.State.INSIDE
		elif self.state == CE_VEH.State.INSIDE and self.get_distance(self) > 50:
			print("INSIDE -> EXITING")
			self.state = CE_VEH.State.EXITING
		elif self.state == CE_VEH.State.EXITING and self.get_distance(self) > 100:
			print("EXITING -> REMOVED")
			self.state = CE_VEH.State.REMOVED

	def show_info(self) -> None:
		print("[CE-VEH] Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))


##############################################################################
#  Ego Cooperative Driving Automation (E-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 특정 주행 미션을 수행하는 주체가 되는 차량
#
##############################################################################

class E_CDA(Vehicle):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		super().__init__(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location)
		self.state = E_CDA.State.INITIAL

	def update_location(self, new_location) -> None:
		super().update_location(new_location)
		self.update_state()

	def create_bsm_plus(self) -> BSMplus:
		bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.get_location())
		return bsm_plus
	
	def create_dmm(self) -> DMM:
		dmm = DMM(self.vehicle_id, self.vehicle_type, self.get_location())
		return dmm
	
	def create_dnm_req(self) -> DNMReq:
		dnm_req = DNMReq(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_req
	
	def create_dnm_resp(self) -> DNMResp:
		dnm_resp = DNMResp(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_resp
	
	def send_bsm(self, channel:Channel) -> None:
		print("BSM+ sent")
		channel.append(self.create_bsm_plus())

	def send_dmm(self, channel:Channel) -> None:
		print("DMM sent")
		channel.append(self.create_dmm())

	def send_dnm_req(self, channel:Channel) -> None:
		print("DNMReq sent")
		channel.append(self.create_dnm_req())

	def send_dnm_resp(self, channel:Channel) -> None:
		print("DNMResp sent")
		channel.append(self.create_dnm_resp())

	def receive_bsm(self, bsm_plus:BSMplus) -> None:
		print("BSM+ received")
		# TODO: process bsm+

	def receive_dmm(self, dmm:DMM) -> None:
		print("DMM_ received")
		# TODO: process dmm

	def receive_dnm_req(self, dnm_req:DNMReq) -> None:
		print("DNMReq received")
		# TODO: process dnm_req

	def receive_dnm_resp(self, dnm_resp:DNMResp) -> None:
		print("DNMResp received")
		# TODO: process dnm_resp

	

	def update_state(self) -> None:
		if self.state == E_CDA.State.INITIAL:
			print("INITIAL -> ADDED")
			self.state = E_CDA.State.ADDED
		elif self.state == E_CDA.State.ADDED and self.get_distance(self) < 100:
			print("ADDED -> APPROACHING")
			self.state = E_CDA.State.APPROACHING
		elif self.state == E_CDA.State.APPROACHING and self.get_distance(self) < 50:
			print("APPROACHING -> INSIDE")
			self.state = E_CDA.State.INSIDE
		elif self.state == E_CDA.State.INSIDE and self.get_distance(self) > 50:
			print("INSIDE -> EXITING")
			self.state = E_CDA.State.EXITING
		elif self.state == E_CDA.State.EXITING and self.get_distance(self) > 100:
			print("EXITING -> REMOVED")
			self.state = E_CDA.State.REMOVED

	def show_info(self) -> None:
		print("[E-CDA] Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))


##############################################################################
#  Target Cooperative Driving Automation (T-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 E-CDA와 주행협상을 수행하는 대상 차량
#
##############################################################################

class T_CDA(Vehicle):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location):
		super().__init__(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, x_location)
		self.state = T_CDA.State.INITIAL

	def update_location(self, new_location) -> None:
		super().update_location(new_location)
		self.update_state()

	def create_bsm_plus(self) -> BSMplus:
		bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.get_location())
		return bsm_plus
	
	def create_dmm(self) -> DMM:
		dmm = DMM(self.vehicle_id, self.vehicle_type, self.get_location())
		return dmm
	
	def create_dnm_req(self) -> DNMReq:
		dnm_req = DNMReq(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_req
	
	def create_dnm_resp(self) -> DNMResp:
		dnm_resp = DNMResp(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_resp
	
	def send_bsm(self, channel:Channel) -> None:
		print("BSM+ sent")
		channel.append(self.create_bsm_plus())

	def send_dmm(self, channel:Channel) -> None:
		print("DMM sent")
		channel.append(self.create_dmm())

	def send_dnm_req(self, channel:Channel) -> None:
		print("DNMReq sent")
		channel.append(self.create_dnm_req())

	def send_dnm_resp(self, channel:Channel) -> None:
		print("DNMResp sent")
		channel.append(self.create_dnm_resp())

	def receive(self) -> None:
		print("Message received")

	def receive_bsm(self, bsm_plus:BSMplus) -> None:
		print("BSM+ received")
		# TODO: process bsm+

	def receive_dmm(self, dmm:DMM) -> None:
		print("DMM_ received")
		# TODO: process dmm

	def receive_dnm_req(self, dnm_req:DNMReq) -> None:
		print("DNMReq received")
		# TODO: process dnm_req

	def receive_dnm_resp(self, dnm_resp:DNMResp) -> None:
		print("DNMResp received")
		# TODO: process dnm_resp


	def update_state(self) -> None:
		if self.state == T_CDA.State.INITIAL:
			print("INITIAL -> ADDED")
			self.state = T_CDA.State.ADDED
		elif self.state == T_CDA.State.ADDED and self.get_distance(self) < 100:
			print("ADDED -> APPROACHING")
			self.state = T_CDA.State.APPROACHING
		elif self.state == T_CDA.State.APPROACHING and self.get_distance(self) < 50:
			print("APPROACHING -> INSIDE")
			self.state = T_CDA.State.INSIDE
		elif self.state == T_CDA.State.INSIDE and self.get_distance(self) > 50:
			print("INSIDE -> EXITING")
			self.state = T_CDA.State.EXITING
		elif self.state == T_CDA.State.EXITING and self.get_distance(self) > 100:
			print("EXITING -> REMOVED")
			self.state = T_CDA.State.REMOVED

	def show_info(self) -> None:
		print("[T-CDA] Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))


