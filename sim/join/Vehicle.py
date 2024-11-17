import os
import sys
import json
import math
import traci
import traci_tool
from enum import Enum
from Channel import Channel, RSU
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp, DetectMessage


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
	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_locaton, vehicle_size):
		self.time_birth		= time_birth
		self.vehicle_id		= vehicle_id
		self.vehicle_type	= vehicle_type
		self.rsu_location	= rsu_locaton
		self.vehicle_size	= vehicle_size
		self.stay = True


##############################################################################
# Normal Vehicle (N-VEH) class
#
# Normal Vehicle, 통신기능 없이 일반 운전자가 주행하는 일반차량
# 전송가능 메시지: 없음
#
##############################################################################

class N_VEH(Vehicle):

	class State(str, Enum):
		INITIAL = "INITIAL"
		ADDED = "ADDED"
		APPROACHING = "APPROACHING"
		INSIDE = "INSIDE"
		EXITING = "EXITING"
		REMOVED = "REMOVED"

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_locaton, vehicle_size):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_locaton, vehicle_size)
		self.state = N_VEH.State.INITIAL
	
	@classmethod
	def from_json(cls, json_data):
		data = json.loads(json_data)
		instance = cls(data['time_birth'], data['vehicle_id'], data['vehicle_type'])
		instance.state = N_VEH.State(data['state'])
		return instance

	def to_dict(self):
		return {
			"time_birth": self.time_birth,
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
			"state": self.state
        }
	
	def show_info(self) -> None:
		print(f"[N-VEH] Vehicle ID: {self.vehicle_id}, Type: {self.vehicle_type}")



##############################################################################
# Connected Vehicle (C-VEH) class
#
#  기본적인 안전 메시지를 송수신하며 일반 운전자가 주행하는 차량 
# 전송가능 메시지: BSM
# (제약사항) 수십 cm이하의 위치정보 제공이 요구됨
#
##############################################################################

class _C_VEH(Vehicle):
		
	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_size):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_size)
		self.vehicle_speed		= vehicle_speed
		self.vehicle_location	= vehicle_location
		self.vehicle_size		= vehicle_size
	
	# New function to calculate distance between vehicle and another vehicle's location as a tuple
	def get_distance_to(self, another_location) -> float:
		return math.sqrt((self.vehicle_location[0] - another_location[0])**2 + (self.vehicle_location[1] - another_location[1])**2)
	
	def get_distance_to_rsu(self) -> float:
		return math.sqrt((self.vehicle_location[0] - self.rsu_location[0])**2 + (self.vehicle_location[1] - self.rsu_location[1])**2)
	

##############################################################################
#  Connected Emergency Vehicle (CE-VEH) class
# 
# 전송가능 메시지: BSM, EDM
# 주변 차량에게 강제적으로 경로변경 요청을 명령할 수 있는 차량
#
##############################################################################
class C_VEH(_C_VEH):

	class State(str, Enum):
		INITIAL = "INITIAL"
		ADDED = "ADDED"
		APPROACHING = "APPROACHING"
		INSIDE = "INSIDE"
		EXITING = "EXITING"
		REMOVED = "REMOVED"
	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_route, vehicle_size, vehicle_edge, vehicle_route_index):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_size)
		
		self.max_speed_normal = 23	# 23 m/s (82.8km/h)
		# self.max_speed_normal = 55.55	# 55.55 m/s (200km/h)
		self.max_speed_emergency = 8.33	# 8.33 m/s (30km/h)
		self.max_speed = self.max_speed_normal
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_route = vehicle_route
		self.vehicle_route_index = vehicle_route_index
		self.vehicle_edge = vehicle_edge
		self.new_event = False
		self.get_edm = False
		self.vehicle_accum_wait_time = 0

		self.state = C_VEH.State.INITIAL

	@classmethod
	def from_json(cls, json_data):
		data = json.loads(json_data)
		instance = cls(data['time_birth'], data['vehicle_id'], data['vehicle_type'], data['rsu_location'], data['vehicle_speed'], data['vehicle_location'])
		instance.state = C_VEH.State(data['state'])
		return instance
	
	def to_dict(self):
		return {
			"time_birth": self.time_birth,
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
			"rsu_location": self.rsu_location,
			"vehicle_speed": self.vehicle_speed,
			"vehicle_location": self.vehicle_location,
			"state": self.state
        }
	
	def update_state(self, step) -> None:
		# print(f"Step({step}) {self.vehicle_id} get_distance_to_rsu: {self.get_distance_to_rsu()}")
		
		if self.state == C_VEH.State.INITIAL:
			# print(f"Step({step}) {self.vehicle_id} INITIAL -> ADDED")
			self.state = C_VEH.State.ADDED
		elif self.state == C_VEH.State.ADDED and self.get_distance_to_rsu() < 200:
			# print(f"Step({step}) {self.vehicle_id} ADDED -> APPROACHING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = C_VEH.State.APPROACHING
		elif self.state == C_VEH.State.APPROACHING and self.get_distance_to_rsu() < 100:
			# print(f"Step({step}) {self.vehicle_id} APPROACHING -> INSIDE, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = C_VEH.State.INSIDE
		elif self.state == C_VEH.State.INSIDE and self.get_distance_to_rsu() > 100:
			# print(f"Step({step}) {self.vehicle_id} INSIDE -> EXITING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = C_VEH.State.EXITING
		elif self.state == C_VEH.State.EXITING and self.get_distance_to_rsu() > 200:
			# print(f"Step({step}) {self.vehicle_id} EXITING -> REMOVED, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = C_VEH.State.REMOVED

	def update(self, new_location, new_speed, new_acceleration, new_lane, new_route, vehicle_edge, vehicle_route_index, vehicle_accumulated_waiting_time) -> None:
		self.stay = True
		self.vehicle_location = new_location
		self.vehicle_speed = new_speed
		self.vehicle_acceleration = new_acceleration
		self.vehicle_lane = new_lane
		self.vehicle_route = new_route
		self.vehicle_edge = vehicle_edge
		self.vehicle_route_index = vehicle_route_index
		self.vehicle_accum_wait_time = vehicle_accumulated_waiting_time
		# print(f"c-veh => lane: {self.vehicle_lane}, route: {self.vehicle_route}, route_index: {self.vehicle_route_index}, edge: {self.vehicle_edge}")
		# print(f"next route: {self.vehicle_route[self.vehicle_route_index]}")
	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None, None, None, None)
		return bsm

	def send_bsm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm())
		# print(f"Step({step}) {self.vehicle_id} sent BSM")

	def receive(self, step, channel:RSU) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(step, message)
				elif isinstance(message, EDM):
					self.receive_edm(step, message)
				elif isinstance(message, BSMplus):
					self.receive_bsm_plus(step, message)
				elif isinstance(message, DetectMessage):
					self.receive_detect_message(step, message)
				else:
					pass
					# print(f"Step({step}) {self.vehicle_id} received a unsupported message({message.msg_type}) sent by {message.sender_vehicle_id}")
		# if self.get_edm == False:
		# 	# print(f"Step({step}) {self.vehicle_id} max_speed {self.max_speed} normal: {self.max_speed_normal}")
		# 	if self.max_speed == 0:
		# 		self.max_speed = self.max_speed_normal
		# 		self.new_event = True
		# self.get_edm = False
	def receive_bsm(self, step, bsm:BSM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM sent by {bsm.sender_vehicle_id}")

	def receive_edm(self, step, edm:EDM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received EDM sent by {edm.sender_vehicle_id}")
		if self.get_distance_to(edm.sender_location) < 100:
			self.get_edm = True
			edm.show_msg()
			vehicle_id = edm.sender_vehicle_id
			
			if len(self.vehicle_route) > self.vehicle_route_index + 1:
				self.next_route = self.vehicle_route[self.vehicle_route_index + 1]
			else:
				self.next_route = None
			
			# print(f"edm next_route : {edm.next_route}")
			if edm.next_route == self.next_route:
				new_speed = traci_tool.edm_process(self.vehicle_id, edm.sender_vehicle_id)
				if new_speed != None:
					self.max_speed = new_speed
				# print(f"Step({step}) {self.vehicle_id} received EDM sent by {edm.sender_vehicle_id}")
				# new_speed = traci_tool.get_slow_down_junction(self.vehicle_id, self.vehicle_edge, self.vehicle_location, slow_distance=200, stop_distance=5)
				# if(new_speed != None):
				# 	self.new_event = True
				# 	self.max_speed = new_speed
			elif self.max_speed != self.max_speed_normal:
				self.max_speed = self.max_speed_normal
				self.new_event = True

		else:
			if self.max_speed != self.max_speed_normal:
				self.max_speed = self.max_speed_normal
				self.new_event = True
	def receive_bsm_plus(self, step, bsm_plus:BSMplus) -> None:
		pass

		if self.get_distance_to(bsm_plus.sender_location) < 100:
			pass

		# print(f"Step({step}) {self.vehicle_id} received BSM+ sent by {bsm_plus.sender_vehicle_id}")
	def receive_detect_message(self, step, detect_message:DetectMessage) -> None:
		pass
		if len(self.vehicle_route) > self.vehicle_route_index + 1:
			self.next_route = self.vehicle_route[self.vehicle_route_index + 1]
		else:
			self.next_route = None
		if (detect_message.sender_vehicle_id is not None) and (detect_message.next_route == self.next_route):
			# print("slow")
			new_speed = traci_tool.get_slow_down_junction(self.vehicle_id, self.vehicle_edge, self.vehicle_location, 200, 5)
			# print(f"slow vehicle id : {self.vehicle_id}, speed:{new_speed}")
			traci.vehicle.setSpeed(self.vehicle_id, new_speed)
			self.max_speed = new_speed
		elif self.max_speed != self.max_speed_normal:
			traci.vehicle.setSpeed(self.vehicle_id, self.max_speed_normal)
			self.max_speed = self.max_speed_normal
		# print(f"Step({step}) {self.vehicle_id} received BSM+ sent by {bsm_plus.sender_vehicle_id}")

	def show_info(self) -> None:
		pass
		# print("Step({}) Vehicle ID: {}, Vehicle Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Connected Emergency Vehicle (CE-VEH) class
# 
# 전송가능 메시지: BSM, EDM
# 주변 차량에게 강제적으로 경로변경 요청을 명령할 수 있는 차량
#
##############################################################################

class CE_VEH(_C_VEH):

	class State(str, Enum):
		INITIAL = "INITIAL"
		ADDED = "ADDED"
		APPROACHING = "APPROACHING"
		INSIDE = "INSIDE"
		EXITING = "EXITING"
		REMOVED = "REMOVED"

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_route, vehicle_size, vehicle_edge, vehicle_route_index):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_size)
		self.time_birth = time_birth
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_route = vehicle_route
		self.vehicle_route_index = vehicle_route_index
		self.vehicle_edge = vehicle_edge
		self.state = CE_VEH.State.INITIAL
		self.vehicle_accum_wait_time = 0

	@classmethod
	def from_json(cls, json_data):
		data = json.loads(json_data)
		instance = cls(data['time_birth'], data['vehicle_id'], data['vehicle_type'], data['rsu_location'], data['vehicle_speed'], data['vehicle_location'])
		instance.state = CE_VEH.State(data['state'])
		return instance

	def to_dict(self):
		return {
			"time_birth": self.time_birth,
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
			"rsu_location": self.rsu_location,
			"vehicle_speed": self.vehicle_speed,
			"vehicle_location": self.vehicle_location,
			"state": self.state
        }
	
	def update_state(self, step) -> None:
		# print(f"Step({step}) {self.vehicle_id} get_distance_to_rsu: {self.get_distance_to_rsu()}")

		if self.state == CE_VEH.State.INITIAL:
			# print(f"Step({step}) {self.vehicle_id} INITIAL -> ADDED")
			self.state = CE_VEH.State.ADDED
		elif self.state == CE_VEH.State.ADDED and self.get_distance_to_rsu() < 200:
			# print(f"Step({step}) {self.vehicle_id} ADDED -> APPROACHING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = CE_VEH.State.APPROACHING
		elif self.state == CE_VEH.State.APPROACHING and self.get_distance_to_rsu() < 100:
			# print(f"Step({step}) {self.vehicle_id} APPROACHING -> INSIDE, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = CE_VEH.State.INSIDE
		elif self.state == CE_VEH.State.INSIDE and self.get_distance_to_rsu() > 100:
			# print(f"Step({step}) {self.vehicle_id} INSIDE -> EXITING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = CE_VEH.State.EXITING
		elif self.state == CE_VEH.State.EXITING and self.get_distance_to_rsu() > 200:
			# print(f"Step({step}) {self.vehicle_id} EXITING -> REMOVED, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = CE_VEH.State.REMOVED

	
	def update(self, new_location, new_speed, new_acceleration, new_lane, new_route, vehicle_edge, vehicle_route_index, vehicle_accumulated_waiting_time) -> None:
		self.stay = True
		self.vehicle_location = new_location
		self.vehicle_speed = new_speed
		self.vehicle_acceleration = new_acceleration
		self.vehicle_lane = new_lane
		self.vehicle_route = new_route
		self.vehicle_route_index = vehicle_route_index
		self.vehicle_edge = vehicle_edge
		self.vehicle_accum_wait_time = vehicle_accumulated_waiting_time
		# print(f"ce-veh => lane: {self.vehicle_lane}, route: {self.vehicle_route}, route_index: {self.vehicle_route_index}, edge: {self.vehicle_edge}")
		# print(f"next route: {self.vehicle_route[self.vehicle_route_index]}")
	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None, None, None, None)
		return bsm

	def create_edm(self) -> EDM:
		if len(self.vehicle_route) > self.vehicle_route_index + 1:
			edm = EDM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, self.vehicle_route[self.vehicle_route_index + 1])
		else:
			edm = EDM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None)
		return edm

	def send_bsm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm())
		# print(f"Step({step}) {self.vehicle_id} sent BSM")

	def send_edm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_edm())
		# print(f"Step({step}) {self.vehicle_id} sent EDM")

	def receive(self, step, channel:RSU) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(step, message)
				elif isinstance(message, EDM):
					self.receive_edm(step, message)
				else:
					print(f"Step({step}) {self.vehicle_id} received a unsupported message({message.msg_type}) sent by {message.sender_vehicle_id}")

	def receive_bsm(self, step, bsm:BSM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM sent by {bsm.sender_vehicle_id}")

	def receive_edm(self, step, edm:EDM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received EDM sent by {edm.sender_vehicle_id}")

	def show_info(self) -> None:
		pass
		# print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Ego Cooperative Driving Automation (E-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 특정 주행 미션을 수행하는 주체가 되는 차량
#
##############################################################################

class E_CDA(_C_VEH):

	class State(str, Enum):
		INITIAL = "INITIAL"
		ADDED = "ADDED"
		APPROACHING = "APPROACHING"
		INSIDE = "INSIDE"
		EXITING = "EXITING"
		REMOVED = "REMOVED"

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_edge, vehicle_route, vehicle_size):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_size)
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_edge = vehicle_edge
		self.vehicle_route = vehicle_route

		self.state = E_CDA.State.INITIAL
	
	@classmethod
	def from_json(cls, json_data):
		data = json.loads(json_data)
		instance = cls(data['time_birth'], data['vehicle_id'], data['vehicle_type'], data['rsu_location'], data['vehicle_speed'], data['vehicle_location'], data['vehicle_acceleration'], data['vehicle_lane'], data['vehicle_route'])
		instance.state = E_CDA.State(data['state'])
		return instance
	
	def to_dict(self):
		return {
			"time_birth": self.time_birth,
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
			"rsu_location": self.rsu_location,
			"vehicle_speed": self.vehicle_speed,
			"vehicle_location": self.vehicle_location,
			"vehicle_acceleration": self.vehicle_acceleration,
			"vehicle_lane": self.vehicle_lane,
			"vehicle_route": self.vehicle_route,
			"state": self.state
        }
	
	def update_state(self, step) -> None:
		# print(f"Step({step}) {self.vehicle_id} get_distance_to_rsu: {self.get_distance_to_rsu()}")
		
		if self.state == E_CDA.State.INITIAL:
			# print(f"Step({step}) {self.vehicle_id} INITIAL -> ADDED")
			self.state = E_CDA.State.ADDED
		elif self.state == E_CDA.State.ADDED and self.get_distance_to_rsu() < 200:
			# print(f"Step({step}) {self.vehicle_id} ADDED -> APPROACHING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = E_CDA.State.APPROACHING
		elif self.state == E_CDA.State.APPROACHING and self.get_distance_to_rsu() < 100:
			# print(f"Step({step}) {self.vehicle_id} APPROACHING -> INSIDE, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = E_CDA.State.INSIDE
		elif self.state == E_CDA.State.INSIDE and self.get_distance_to_rsu() > 100:
			# print(f"Step({step}) {self.vehicle_id} INSIDE -> EXITING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = E_CDA.State.EXITING
		elif self.state == E_CDA.State.EXITING and self.get_distance_to_rsu() > 200:
			# print(f"Step({step}) {self.vehicle_id} EXITING -> REMOVED, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = E_CDA.State.REMOVED
	

	def update(self, new_location, new_speed, new_acceleration, new_lane, new_edge, new_route) -> None:
		self.stay = True
		self.vehicle_location = new_location
		self.vehicle_speed = new_speed
		self.vehicle_acceleration = new_acceleration
		self.vehicle_lane = new_lane
		self.vehicle_edge = new_edge
		self.vehicle_route = new_route

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None, None, None, None)
		return bsm

	def create_bsm_plus(self) -> BSMplus:
		bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, self.vehicle_acceleration, self.vehicle_lane, self.vehicle_edge, self.vehicle_route, None, None, None, None, None)
		return bsm_plus
	
	def create_dmm(self) -> DMM:
		dmm = DMM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, self.vehicle_acceleration, self.vehicle_lane, None)
		return dmm
	
	def create_dnm_req(self) -> DNMReq:
		dnm_req = DNMReq(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, None, None, None, None)
		return dnm_req
	
	def create_dnm_resp(self) -> DNMResp:
		dnm_resp = DNMResp(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, None, None, None, None)
		return dnm_resp
	
	def send_bsm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm())
		# print(f"Step({step}) {self.vehicle_id} sent BSM")
	
	def send_bsm_plus(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm_plus())
		# print(f"Step({step}) {self.vehicle_id} sent BSM+")

	def send_dmm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dmm())
		# print(f"Step({step}) {self.vehicle_id} sent DMM")

	def send_dnm_req(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dnm_req())
		# print(f"Step({step}) {self.vehicle_id} sent DNMReq")

	def send_dnm_resp(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dnm_resp())
		# print(f"Step({step}) {self.vehicle_id} sent DNMResp")

	def receive(self, step, channel:RSU) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(step, message)
				elif isinstance(message, BSMplus):
					self.receive_bsm_plus(step, message)
				elif isinstance(message, EDM):
					self.receive_edm(step, message)
				elif isinstance(message, DMM):
					self.receive_dmm(step, message)
				elif isinstance(message, DNMReq):
					self.receive_dnm_req(step, message)
				elif isinstance(message, DNMResp):
					self.receive_dnm_resp(step, message)
				elif isinstance(message, DetectMessage):
					self.receive_detect_message(step, message)
				else:
					print(f"Step({step}) {self.vehicle_id} received a unsupported message({message.msg_type}) sent by {message.sender_vehicle_id}")

	def receive_bsm(self, step, bsm:BSM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM sent by {bsm.sender_vehicle_id}")

	def receive_bsm_plus(self, step, bsm_plus:BSMplus) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM+ sent by {bsm_plus.sender_vehicle_id}")

	def receive_edm(self, step, edm:EDM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received EDM sent by {edm.sender_vehicle_id}")

	def receive_dmm(self, step, dmm:DMM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DMM sent by {dmm.sender_vehicle_id}")

	def receive_dnm_req(self, step, dnm_req:DNMReq) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DNMReq sent by {dnm_req.sender_vehicle_id}")

	def receive_dnm_resp(self, step, dnm_resp:DNMResp) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DNMResp sent by {dnm_resp.sender_vehicle_id}")
	def receive_detect_message(self, step, detect_msg:DetectMessage) -> None:
		
		pass

	def show_info(self) -> None:
		pass
		# print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.get_distance()))


##############################################################################
#  Target Cooperative Driving Automation (T-CDA) class
# 
# 전송가능 메시지: BSM+, DMM, DNM
# 주행협상 시나리오에서 E-CDA와 주행협상을 수행하는 대상 차량
#
##############################################################################

class T_CDA(_C_VEH):

	class State(str, Enum):
		INITIAL = "INITIAL"
		ADDED = "ADDED"
		APPROACHING = "APPROACHING"
		INSIDE = "INSIDE"
		EXITING = "EXITING"
		REMOVED = "REMOVED"

	def __init__(self, time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, new_edge, vehicle_route, vehicle_size):
		super().__init__(time_birth, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_size)
		self.vehicle_acceleration = vehicle_acceleration
		self.vehicle_lane = vehicle_lane
		self.vehicle_edge = new_edge
		self.vehicle_route = vehicle_route

		self.state = T_CDA.State.INITIAL
	
	@classmethod
	def from_json(cls, json_data):
		data = json.loads(json_data)
		instance = cls(data['time_birth'], data['vehicle_id'], data['vehicle_type'], data['rsu_location'], data['vehicle_speed'], data['vehicle_location'], data['vehicle_acceleration'], data['vehicle_lane'], data['vehicle_route'])
		instance.state = T_CDA.State(data['state'])
		return instance
	
	def to_dict(self):
		return {
            "time_birth": self.time_birth,
			"vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
            "rsu_location": self.rsu_location,
			"vehicle_speed": self.vehicle_speed,
			"vehicle_location": self.vehicle_location,
			"vehicle_acceleration": self.vehicle_acceleration,
			"vehicle_lane": self.vehicle_lane,
			"vehicle_route": self.vehicle_route,
			"state": self.state
        }
	
	def update_state(self, step) -> None:
		# print(f"Step({step}) {self.vehicle_id} get_distance_to_rsu: {self.get_distance_to_rsu()}")
		
		if self.state == T_CDA.State.INITIAL:
			# print(f"Step({step}) {self.vehicle_id} INITIAL -> ADDED")
			self.state = T_CDA.State.ADDED
		elif self.state == T_CDA.State.ADDED and self.get_distance_to_rsu() < 200:
			# print(f"Step({step}) {self.vehicle_id} ADDED -> APPROACHING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = T_CDA.State.APPROACHING
		elif self.state == T_CDA.State.APPROACHING and self.get_distance_to_rsu() < 100:
			# print(f"Step({step}) {self.vehicle_id} APPROACHING -> INSIDE, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = T_CDA.State.INSIDE
		elif self.state == T_CDA.State.INSIDE and self.get_distance_to_rsu() > 100:
			# print(f"Step({step}) {self.vehicle_id} INSIDE -> EXITING, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = T_CDA.State.EXITING
		elif self.state == T_CDA.State.EXITING and self.get_distance_to_rsu() > 200:
			# print(f"Step({step}) {self.vehicle_id} EXITING -> REMOVED, get_distance_to_rsu: {self.get_distance_to_rsu()}")
			self.state = T_CDA.State.REMOVED

	def update(self, new_location, new_speed, new_acceleration, new_lane, new_edge, new_route) -> None:
		self.stay = True
		self.vehicle_location = new_location
		self.vehicle_speed = new_speed
		self.vehicle_acceleration = new_acceleration
		self.vehicle_lane = new_lane
		self.vehicle_edge = new_edge
		self.vehicle_route = new_route

	# def update(self, new_location, new_speed) -> None:
	# def get_location(self) -> tuple:
	# def get_distance(self) -> float:
	# def get_speed(self) -> float:
	
	def create_bsm(self) -> BSM:
		bsm = BSM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None, None, None, None)
		return bsm

	def create_bsm_plus(self) -> BSMplus:
		if self.vehicle_speed == 0:
			# print(f"car accident")
			bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, self.vehicle_acceleration, self.vehicle_lane, self.vehicle_edge, self.vehicle_route, None, None, None, None, None, True)
		else:
			bsm_plus = BSMplus(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, self.vehicle_acceleration, self.vehicle_lane, self.vehicle_edge, self.vehicle_route, None, None, None, None, None, False)
		return bsm_plus
	
	def receive_edm(self, step, edm:EDM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received EDM sent by {edm.sender_vehicle_id}")

	def create_dmm(self) -> DMM:
		dmm = DMM(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None)
		return dmm
	
	def create_dnm_req(self) -> DNMReq:
		dnm_req = DNMReq(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None)
		return dnm_req
	
	def create_dnm_resp(self) -> DNMResp:
		dnm_resp = DNMResp(self.vehicle_id, self.vehicle_type, self.rsu_location, self.vehicle_speed, self.vehicle_location, self.vehicle_size, None, None, None)
		return dnm_resp
	
	def send_bsm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm())
		# print(f"Step({step}) {self.vehicle_id} sent BSM")

	def send_bsm_plus(self, step, channel:RSU) -> None:
		channel.add_message(self.create_bsm_plus())
		# print(f"Step({step}) {self.vehicle_id} sent BSM+")

	def send_dmm(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dmm())
		# print(f"Step({step}) {self.vehicle_id} sent DMM")

	def send_dnm_req(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dnm_req())
		# print(f"Step({step}) {self.vehicle_id} sent DNMReq")

	def send_dnm_resp(self, step, channel:RSU) -> None:
		channel.add_message(self.create_dnm_resp())
		# print(f"Step({step}) {self.vehicle_id} sent DNMResp")

	def receive(self, step, channel:RSU) -> None:
		for message in channel.messages:
			if message.sender_vehicle_id != self.vehicle_id:
				if isinstance(message, BSM):
					self.receive_bsm(step, message)
				elif isinstance(message, BSMplus):
					self.receive_bsm_plus(step, message)
				elif isinstance(message, EDM):
					self.receive_edm(step, message)
				elif isinstance(message, DMM):
					self.receive_dmm(step, message)
				elif isinstance(message, DNMReq):
					self.receive_dnm_req(step, message)
				elif isinstance(message, DNMResp):
					self.receive_dnm_resp(step, message)
				else:
					pass
					# print(f"Step({step}) {self.vehicle_id} received a unsupported message({message.msg_type}) sent by {message.sender_vehicle_id}")

	def receive_bsm(self, step, bsm_plus:BSM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM sent by {bsm_plus.sender_vehicle_id}")
		# TODO: process bsm

	def receive_bsm_plus(self, step, bsm_plus:BSMplus) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received BSM+ sent by {bsm_plus.sender_vehicle_id}")
		# TODO: process bsm+

	def receive_dmm(self, step, dmm:DMM) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DMM sent by {dmm.sender_vehicle_id}")
		# TODO: process dmm

	def receive_dnm_req(self, step, dnm_req:DNMReq) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DNMReq sent by {dnm_req.sender_vehicle_id}")
		# TODO: process dnm_req

	def receive_dnm_resp(self, step, dnm_resp:DNMResp) -> None:
		pass
		# print(f"Step({step}) {self.vehicle_id} received DNMResp sent by {dnm_resp.sender_vehicle_id}")
		# TODO: process dnm_resp

	def show_info(self) -> None:
		pass
		# print("Step({}) Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(GlobalSim.step, self.vehicle_id, self.vehicle_type, self.state, self.distance))


