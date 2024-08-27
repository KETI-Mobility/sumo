import os
import sys
import traci
import math
from enum import Enum
from Channel import Channel
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
import GlobalSim

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
	def __init__(self, time_birth, vehicle_id, vehicle_type):
		self.time_birth = time_birth
		self.vehicle_id = vehicle_id
		self.vehicle_type = vehicle_type
		self.stay = True

	def show_info(self) -> None:
		print("Vehicle ID: {}, Type: {}".format(self.vehicle_id, self.vehicle_type))


##############################################################################
# Normal Vehicle (N-VEH) class
#
# Normal Vehicle, 통신기능 없이 일반 운전자가 주행하는 일반차량
# 전송가능 메시지: 없음
#
##############################################################################

class N_VEH(Vehicle):

	def __init__(self, time_birth, vehicle_id, vehicle_type):
		super().__init__(time_birth, vehicle_id, vehicle_type)
		self.state = N_VEH.State.INITIAL

	def show_info(self) -> None:
		print("[N-VEH] Vehicle ID: {}, Type: {}".format(self.vehicle_id, self.vehicle_type))



##############################################################################
# Connected Vehicle (C-VEH) class
#
#  기본적인 안전 메시지를 송수신하며 일반 운전자가 주행하는 차량 
# 전송가능 메시지: BSM
# (제약사항) 수십 cm이하의 위치정보 제공이 요구됨
#
##############################################################################

class _C_VEH(Vehicle):

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location):
		super().__init__(time_birth, vehicle_id, vehicle_type)
		self.rsu_location = rsu_location
		self.vehicle_speed = vehicle_speed
		self.vehicle_location = vehicle_location
		
	def update(self, new_location, new_speed) -> None:
		self.stay = True
		self.vehicle_location = new_location
		self.vehicle_speed = new_speed
	
	def get_location(self) -> tuple:
		return self.vehicle_location 
	
	def get_distance(self) -> float:
		return math.sqrt((self.vehicle_location[0] - self.rsu_location[0])**2 + (self.vehicle_location[1] - self.rsu_location[1])**2)
	
	def get_speed(self) -> float:
		return self.vehicle_speed
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.vehicle_location, self.vehicle_speed)
		return bsm

	def send_bsm(self, channel:Channel) -> None:
		channel.add_message(self.create_bsm())
		print("Step({}) Vehicle id:{}: BSM sent".format(GlobalSim.step, self.vehicle_id))

##############################################################################
#  Connected Emergency Vehicle (CE-VEH) class
# 
# 전송가능 메시지: BSM, EDM
# 주변 차량에게 강제적으로 경로변경 요청을 명령할 수 있는 차량
#
##############################################################################
class C_VEH(_C_VEH):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location)
		
		self.state = C_VEH.State.INITIAL

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	# def create_bsm(self) -> BSM:
	# def send_bsm(self, channel:Channel) -> None:
	
	def receive(self, channel:Channel) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(message)
				else:
					print("Step({}) Vehicle id:{}: Unknown message type".format(GlobalSim.step, self.vehicle_id))

	def receive_bsm(self, bsm:BSM) -> None:
		print("Step({}) Vehicle id:{}: BSM received".format(GlobalSim.step, self.vehicle_id))

		bsm.show_msg()
		# TODO: process bsm
		

	def update_state(self) -> None:
		if self.state == C_VEH.State.INITIAL:
			print("Step({}) INITIAL -> ADDED".format(GlobalSim.step))
			self.state = C_VEH.State.ADDED
		elif self.state == C_VEH.State.ADDED and self.get_distance(self) < 100:
			print("Step({}) ADDED -> APPROACHING".format(GlobalSim.step))
			self.state = C_VEH.State.APPROACHING
		elif self.state == C_VEH.State.APPROACHING and self.get_distance(self) < 50:
			print("Step({}) APPROACHING -> INSIDE".format(GlobalSim.step, ))
			self.state = C_VEH.State.INSIDE
		elif self.state == C_VEH.State.INSIDE and self.get_distance(self) > 50:
			print("Step({}) INSIDE -> EXITING".format(GlobalSim.step))
			self.state = C_VEH.State.EXITING
		elif self.state == C_VEH.State.EXITING and self.get_distance(self) > 100:
			print("Step({}) EXITING -> REMOVED".format(GlobalSim.step))
			self.state = C_VEH.State.REMOVED

	def show_info(self) -> None:
		print("Step({}) Vehicle ID: {}, Vehicle Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Connected Emergency Vehicle (CE-VEH) class
# 
# 전송가능 메시지: BSM, EDM
# 주변 차량에게 강제적으로 경로변경 요청을 명령할 수 있는 차량
#
##############################################################################

class CE_VEH(_C_VEH):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location)

		self.state = CE_VEH.State.INITIAL

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	# def create_bsm(self) -> BSM:
	# def send_bsm(self, channel:Channel) -> None:
	
	def create_edm(self) -> EDM:
		edm = EDM(self.vehicle_id, self.vehicle_type, self.get_location())
		return edm

	def send_edm(self, channel:Channel) -> None:
		channel.add_message(self.create_edm())
		print("Step({}) Vehicle {}: EDM sent".format(GlobalSim.step, self.vehicle_id))

	def receive(self, channel:Channel) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(message)
				elif isinstance(message, EDM):
					self.receive_edm(message)
				else:
					print("Step({}) Vehicle {}: Unknown message type".format(GlobalSim.step, self.vehicle_id))

	def receive_bsm(self, bsm:BSM) -> None:
		print("Step({}) Vehicle id:{}: BSM received".format(GlobalSim.step, self.vehicle_id))

		bsm.show_msg()
		# TODO: process BSM

	def receive_edm(self, edm:EDM) -> None:
		print("Step({}) Vehicle id:{}: EDM received".format(GlobalSim.step, self.vehicle_id))

		edm.show_msg()
		# TODO: process edm

	def update_state(self) -> None:
		if self.state == CE_VEH.State.INITIAL:
			print("Step({}) INITIAL -> ADDED".format(GlobalSim.step))
			self.state = CE_VEH.State.ADDED
		elif self.state == CE_VEH.State.ADDED and self.get_distance(self) < 100:
			print("Step({}) ADDED -> APPROACHING".format(GlobalSim.step))
			self.state = CE_VEH.State.APPROACHING
		elif self.state == CE_VEH.State.APPROACHING and self.get_distance(self) < 50:
			print("Step({}) APPROACHING -> INSIDE".format(GlobalSim.step))
			self.state = CE_VEH.State.INSIDE
		elif self.state == CE_VEH.State.INSIDE and self.get_distance(self) > 50:
			print("Step({}) INSIDE -> EXITING".format(GlobalSim.step))
			self.state = CE_VEH.State.EXITING
		elif self.state == CE_VEH.State.EXITING and self.get_distance(self) > 100:
			print("Step({}) EXITING -> REMOVED".format(GlobalSim.step))
			self.state = CE_VEH.State.REMOVED

	def show_info(self) -> None:
		print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Ego Cooperative Driving Automation (E-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 특정 주행 미션을 수행하는 주체가 되는 차량
#
##############################################################################

class E_CDA(_C_VEH):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_route):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location)
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_route = vehicle_route

		self.state = E_CDA.State.INITIAL

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	# def create_bsm(self) -> BSM:
	# def send_bsm(self, channel:Channel) -> None:
	
	def create_bsm_plus(self) -> BSMplus:
		bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_acceleration, self.vehicle_lane, self.vehicle_route)
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
	
	def send_bsm_plus(self, channel:Channel) -> None:
		channel.add_message(self.create_bsm_plus())
		print("Step({}) Vehicle {}: BSM+ sent".format(GlobalSim.step, self.vehicle_id))

	def send_dmm(self, channel:Channel) -> None:
		channel.add_message(self.create_dmm())
		print("Step({}) Vehicle {}: DMM sent".format(GlobalSim.step, self.vehicle_id))

	def send_dnm_req(self, channel:Channel) -> None:
		channel.add_message(self.create_dnm_req())
		print("Step({}) Vehicle {}: DNMReq sent".format(GlobalSim.step, self.vehicle_id))

	def send_dnm_resp(self, channel:Channel) -> None:
		channel.add_message(self.create_dnm_resp())
		print("Step({}) Vehicle {}: DNMResp sent".format(GlobalSim.step, self.vehicle_id))

	def receive(self, channel:Channel) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(message)
				elif isinstance(message, BSMplus):
					self.receive_bsm_plus(message)
				elif isinstance(message, DMM):
					self.receive_dmm(message)
				elif isinstance(message, DNMReq):
					self.receive_dnm_req(message)
				elif isinstance(message, DNMResp):
					self.receive_dnm_resp(message)
				else:
					print("Step({}) Vehicle {}: Unknown message type".format(GlobalSim.step, self.vehicle_id))

	def receive_bsm(self, bsm:BSM) -> None:
		print("Step({}) Vehicle id:{}: BSM received".format(GlobalSim.step, self.vehicle_id))

		bsm.show_msg()
		# TODO: process BSM

	def receive_bsm_plus(self, bsm_plus:BSMplus) -> None:
		print("Step({}) Vehicle id:{}: BSM+ received".format(GlobalSim.step, self.vehicle_id))

		bsm_plus.show_msg()
		# TODO: process BSM+

	def receive_dmm(self, dmm:DMM) -> None:
		print("Step({}) Vehicle id:{}: DMM received".format(GlobalSim.step, self.vehicle_id))

		dmm.show_msg()
		# TODO: process DMM

	def receive_dnm_req(self, dnm_req:DNMReq) -> None:
		print("Step({}) Vehicle id:{}: DNMReq received".format(GlobalSim.step, self.vehicle_id))

		dnm_req.show_msg()
		# TODO: process DNMReq

	def receive_dnm_resp(self, dnm_resp:DNMResp) -> None:
		print("Step({}) Vehicle id:{}: DNMResp received".format(GlobalSim.step, self.vehicle_id))
		
		dnm_resp.show_msg()
		# TODO: process DNMResp
	
	def update_state(self) -> None:
		if self.state == E_CDA.State.INITIAL:
			print("Step({}) INITIAL -> ADDED".format(GlobalSim.step))
			self.state = E_CDA.State.ADDED
		elif self.state == E_CDA.State.ADDED and self.get_distance(self) < 100:
			print("Step({}) ADDED -> APPROACHING".format(GlobalSim.step))
			self.state = E_CDA.State.APPROACHING
		elif self.state == E_CDA.State.APPROACHING and self.get_distance(self) < 50:
			print("Step({}) APPROACHING -> INSIDE".format(GlobalSim.step))
			self.state = E_CDA.State.INSIDE
		elif self.state == E_CDA.State.INSIDE and self.get_distance(self) > 50:
			print("Step({}) INSIDE -> EXITING".format(GlobalSim.step))
			self.state = E_CDA.State.EXITING
		elif self.state == E_CDA.State.EXITING and self.get_distance(self) > 100:
			print("Step({}) EXITING -> REMOVED".format(GlobalSim.step))
			self.state = E_CDA.State.REMOVED

	def show_info(self) -> None:
		print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Target Cooperative Driving Automation (T-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 E-CDA와 주행협상을 수행하는 대상 차량
#
##############################################################################

class T_CDA(_C_VEH):

	class State(Enum):
		INITIAL = 1
		ADDED = 2
		APPROACHING = 3
		INSIDE = 4
		EXITING = 5
		REMOVED = 6

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_route):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location)
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_route = vehicle_route

		self.state = T_CDA.State.INITIAL

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	# def create_bsm(self) -> BSM:
	# def send_bsm(self, channel:Channel) -> None:

	def create_bsm_plus(self) -> BSMplus:
		bsm = BSMplus(self.vehicle_id, self.vehicle_type, self.get_location())
		return bsm
	
	def create_dmm(self) -> DMM:
		dmm = DMM(self.vehicle_id, self.vehicle_type, self.get_location())
		return dmm
	
	def create_dnm_req(self) -> DNMReq:
		dnm_req = DNMReq(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_req
	
	def create_dnm_resp(self) -> DNMResp:
		dnm_resp = DNMResp(self.vehicle_id, self.vehicle_type, self.get_location())
		return dnm_resp
	
	def send_bsm_plus(self, channel:Channel) -> None:
		channel.add_message(self.create_bsm())
		print("Step({}) Vehicle {}: BSM+ sent".format(GlobalSim.step, self.vehicle_id))

	def send_dmm(self, channel:Channel) -> None:
		channel.add_message(self.create_dmm())
		print("Step({}) Vehicle {}: DMM sent".format(GlobalSim.step, self.vehicle_id))

	def send_dnm_req(self, channel:Channel) -> None:
		channel.add_message(self.create_dnm_req())
		print("Step({}) Vehicle {}: DNMReq sent".format(GlobalSim.step, self.vehicle_id))

	def send_dnm_resp(self, channel:Channel) -> None:
		channel.add_message(self.create_dnm_resp())
		print("Step({}) Vehicle {}: DNMResp sent".format(GlobalSim.step, self.vehicle_id))

	def receive(self, channel:Channel) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSMplus):
					self.receive_bsm(message)
				elif isinstance(message, DMM):
					self.receive_dmm(message)
				elif isinstance(message, DNMReq):
					self.receive_dnm_req(message)
				elif isinstance(message, DNMResp):
					self.receive_dnm_resp(message)
				else:
					print("Step({}) Vehicle {}: Unknown message type".format(GlobalSim.step, self.vehicle_id))

	def receive_bsm(self, bsm_plus:BSMplus) -> None:
		print("Step({}) Vehicle {}: BSM+ received".format(GlobalSim.step, self.vehicle_id))
		# TODO: process bsm+

	def receive_dmm(self, dmm:DMM) -> None:
		print("Step({}) Vehicle {}: DMM received".format(GlobalSim.step, self.vehicle_id))
		# TODO: process dmm

	def receive_dnm_req(self, dnm_req:DNMReq) -> None:
		print("Step({}) Vehicle {}: DNMReq received".format(GlobalSim.step, self.vehicle_id))
		# TODO: process dnm_req

	def receive_dnm_resp(self, dnm_resp:DNMResp) -> None:
		print("Step({}) Vehicle {}: DNMResp received".format(GlobalSim.step, self.vehicle_id))
		# TODO: process dnm_resp

	def update_state(self) -> None:
		if self.state == T_CDA.State.INITIAL:
			print("Step({}) INITIAL -> ADDED".format(GlobalSim.step))
			self.state = T_CDA.State.ADDED
		elif self.state == T_CDA.State.ADDED and self.get_distance(self) < 100:
			print("Step({}) ADDED -> APPROACHING".format(GlobalSim.step))
			self.state = T_CDA.State.APPROACHING
		elif self.state == T_CDA.State.APPROACHING and self.get_distance(self) < 50:
			print("Step({}) APPROACHING -> INSIDE".format(GlobalSim.step))
			self.state = T_CDA.State.INSIDE
		elif self.state == T_CDA.State.INSIDE and self.get_distance(self) > 50:
			print("Step({}) INSIDE -> EXITING".format(GlobalSim.step))
			self.state = T_CDA.State.EXITING
		elif self.state == T_CDA.State.EXITING and self.get_distance(self) > 100:
			print("Step({}) EXITING -> REMOVED".format(GlobalSim.step))
			self.state = T_CDA.State.REMOVED

	def show_info(self) -> None:
		print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.distance))


