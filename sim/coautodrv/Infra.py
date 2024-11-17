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
		self.detected_vehicle_id = ""
		

class CCTV(Infra):
	
	def __init__(self, time_birth, infra_id, rsu_locaton, location, detect_edge):
		super().__init__(time_birth, infra_id, location)
		self.detect_edge = detect_edge
		self.rsu_location = rsu_locaton
		self.infra_type = Infra.Type.CCTV
		


	def detection(self) -> None:
		vehicles = traci.edge.getLastStepVehicleIDs(self.detect_edge)
		if vehicles != None:
			for vehicle in vehicles:
				self.detected_vehicle_id = vehicle
				

	def create_detect_message(self) -> DetectMessage:
		vehicle_type = traci.vehicle.getTypeID(self.detected_vehicle_id)
		vehicle_speed = traci.vehicle.getSpeed(self.detected_vehicle_id)
		vehicle_location = traci.vehicle.getPosition(self.detected_vehicle_id)
		vehicle_acceleration = traci.vehicle.getAcceleration(self.detected_vehicle_id)
		bsm_plus = DetectMessage(self.infra_type, self.detected_vehicle_id, vehicle_type, self.rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, self.detect_edge)
		return bsm_plus

	def send_detect_message(self, step, channel:RSU):
		if self.detected_vehicle_id is not None:
		    channel.add_message(self.create_detect_message())
			

        
        
		
    
		