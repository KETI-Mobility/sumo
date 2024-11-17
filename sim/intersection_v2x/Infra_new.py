import os
import sys
import json
import math
import traci
import traci_tool
from enum import Enum
from Channel import Channel, RSU
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp, DetectMessage



class Infra:
	
	class Type(Enum):
		NONE	= 0
		CCTV     = 1
		TL = 2
		
	def __init__(self, time_birth, infra_id, locaton):
		self.time_birth		= time_birth
		self.infra_id		= infra_id
		self.location	= locaton
		self.detected_vehicle_id = None
		self.infra_type = Infra.Type.NONE
		

class CCTV(Infra):
	
	def __init__(self, time_birth, infra_id, rsu_locaton, location, detect_edge):
		super().__init__(time_birth, infra_id, location)
		self.detect_edge = detect_edge
		self.rsu_location = rsu_locaton
		self.infra_type = Infra.Type.CCTV
		


	def detection(self) -> None:
		vehicles = traci.edge.getLastStepVehicleIDs(self.detect_edge)
		# print(f"len: {len(vehicles)}")
		if len(vehicles) > 0:
			# print(f"detect v: {vehicles}")
			for vehicle in vehicles:
				self.detected_vehicle_id = vehicle
		else:
			self.detected_vehicle_id = None

	def create_detect_message(self) -> DetectMessage:
		if self.detected_vehicle_id is not None:
			vehicle_type = traci.vehicle.getTypeID(self.detected_vehicle_id)
			vehicle_speed = traci.vehicle.getSpeed(self.detected_vehicle_id)
			vehicle_location = traci.vehicle.getPosition(self.detected_vehicle_id)
			vehicle_acceleration = traci.vehicle.getAcceleration(self.detected_vehicle_id)
			vehicle_route = traci.vehicle.getRoute(self.detected_vehicle_id)
			vehicle_route_index = traci.vehicle.getRouteIndex(self.detected_vehicle_id)
			# print(f"route : {vehicle_route}, index: {vehicle_route_index}")
			bsm_plus = DetectMessage(self.infra_type, self.detected_vehicle_id, vehicle_type, self.rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, self.detect_edge, vehicle_route[vehicle_route_index + 1])
		else:
			bsm_plus = DetectMessage(self.infra_type, self.detected_vehicle_id, None, self.rsu_location, None, None, None, self.detect_edge, None)
		
		return bsm_plus

	def send_detect_message(self, step, channel:RSU):
			# print(f"send detect message")
		channel.add_message(self.create_detect_message())
			

        

class CCTV(Infra):
	
	def __init__(self, time_birth, infra_id, rsu_locaton, location, detect_edge):
		super().__init__(time_birth, infra_id, location)
		self.detect_edge = detect_edge
		self.rsu_location = rsu_locaton
		self.infra_type = Infra.Type.CCTV
		


	def detection(self) -> None:
		vehicles = traci.edge.getLastStepVehicleIDs(self.detect_edge)
		# print(f"len: {len(vehicles)}")
		if len(vehicles) > 0:
			# print(f"detect v: {vehicles}")
			for vehicle in vehicles:
				self.detected_vehicle_id = vehicle
		else:
			self.detected_vehicle_id = None

	def create_detect_message(self) -> DetectMessage:
		if self.detected_vehicle_id is not None:
			vehicle_type = traci.vehicle.getTypeID(self.detected_vehicle_id)
			vehicle_speed = traci.vehicle.getSpeed(self.detected_vehicle_id)
			vehicle_location = traci.vehicle.getPosition(self.detected_vehicle_id)
			vehicle_acceleration = traci.vehicle.getAcceleration(self.detected_vehicle_id)
			vehicle_route = traci.vehicle.getRoute(self.detected_vehicle_id)
			vehicle_route_index = traci.vehicle.getRouteIndex(self.detected_vehicle_id)
			# print(f"route : {vehicle_route}, index: {vehicle_route_index}")
			bsm_plus = DetectMessage(self.infra_type, self.detected_vehicle_id, vehicle_type, self.rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, self.detect_edge, vehicle_route[vehicle_route_index + 1])
		else:
			bsm_plus = DetectMessage(self.infra_type, self.detected_vehicle_id, None, self.rsu_location, None, None, None, self.detect_edge, None)
		
		return bsm_plus

	def send_detect_message(self, step, channel:RSU):
			# print(f"send detect message")
		channel.add_message(self.create_detect_message())
			

        
class TrafficLight(Infra):
	class State(Enum):
		GUARANTEED_TIME	= 0
		EXTENDED_TIME     = 1
		YELLOW = 2

	def __init__(self, time_birth, infra_id, rsu_locaton, location):
		super().__init__(time_birth, infra_id, location)
		self.rsu_location = rsu_locaton
		self.infra_type = Infra.Type.TL
		self.edges = []
		self.max_waiting_time = 0
		self.current_state = None
		self.current_edge_id = None
		self.next_edge_id = None
		self.max_vehicle_id = None
		self.until = 0
		self.vehicle_on_current_edge = False
		self.debug_max_waiting_time = 0
		self.state = self.State.YELLOW
	
	def set_edges(self):
		controlled_lanes = traci.trafficlight.getControlledLanes(self.infra_id)
		for lane in controlled_lanes:
			the_lane = traci.lane.getEdgeID(lane)
			if self.edges.__contains__(the_lane) == False:
				self.edges.append(the_lane)

	def receive(self, step, channel:RSU) -> None:
		self.vehicle_on_current_edge = False
		self.max_waiting_time = 0
		for message in channel.messages:
			if isinstance(message, BSM):
				self.receive_bsm(step, message)
			else:
				pass
				# print(f"Step({step}) {self.infra_id} received a unsupported message({message.msg_type}) sent by {message.sender_vehicle_id}")

	def receive_bsm(self, step, bsm:BSM) -> None:
		if bsm.sender_edge_id.find(":") != -1:
			# print(f"internal")
			# print(f"bsm.sender_edge_id: {bsm.sender_edge_id}")
			pass
		else:
			if self.current_edge_id != None:
				if (self.current_edge_id == bsm.sender_edge_id) and (bsm.sender_waiting_time != 0):
					self.vehicle_on_current_edge = True
					# print("on vehicle")
				
			if self.max_waiting_time < bsm.sender_waiting_time:
				self.max_waiting_time = bsm.sender_waiting_time
				self.max_vehicle_id = bsm.sender_vehicle_id
				self.next_edge_id = bsm.sender_edge_id
				if self.max_waiting_time > self.debug_max_waiting_time:
					self.debug_max_waiting_time = self.max_waiting_time
				# print(f"max_waiting_time : {self.max_waiting_time}, next_edge_id: {self.next_edge_id}")
		
	def set_state(self, step):
		# print(f"step: {step}, until: {self.until}")
		if self.next_edge_id != None:
			index = self.edges.index(self.next_edge_id)
	
			if self.state == self.State.GUARANTEED_TIME:
				if step >= self.until:
					if traci.edge.getLastStepVehicleNumber(self.current_edge_id) > 10:
						self.state = self.State.EXTENDED_TIME
						self.until = step + 5
					elif self.current_edge_id != self.next_edge_id:
						self.state = self.State.YELLOW
						traci.trafficlight.setPhase(self.infra_id, self.current_state + 1)
						self.current_state = self.current_state + 1
						self.until = step + 5
			elif self.state == self.State.EXTENDED_TIME:
				if step >= self.until:
					if self.current_edge_id != self.next_edge_id:
						self.state = self.State.YELLOW
						traci.trafficlight.setPhase(self.infra_id, self.current_state + 1)
						self.current_state = self.current_state + 1
						self.until = step + 5
			elif self.state == self.State.YELLOW:
				if step >= self.until:
					self.state = self.State.GUARANTEED_TIME
					traci.trafficlight.setPhase(self.infra_id, index * 2)
					self.until = step + 5
					self.current_state = index * 2
					self.current_edge_id = self.next_edge_id



        
		
