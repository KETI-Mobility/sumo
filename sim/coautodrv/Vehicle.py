import os
import sys
import traci
import math
from enum import Enum


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

	def update_location(self, new_location):
		self.cur_location = new_location

	def get_distance(self):
		self.distance = math.sqrt((self.x_location[0] - self.cur_location[0])**2 + (self.x_location[1] - self.cur_location[1])**2)
		return self.distance
	
	def show_info(self):
		print("Vehicle ID: {}, Type: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.distance))

