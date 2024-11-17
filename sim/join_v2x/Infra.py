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
		pass
			# print(f"send detect message")
		channel.add_message(self.create_detect_message())
			

        
        
		
    
		