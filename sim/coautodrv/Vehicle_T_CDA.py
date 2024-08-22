import os
import sys
import traci
import math
from enum import Enum
from Vehicle import Vehicle


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

	def update_location(self, new_location):
		super().update_location(new_location)
		self.update_state()

	def update_state(self):
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

	def show_info(self):
		print("Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))