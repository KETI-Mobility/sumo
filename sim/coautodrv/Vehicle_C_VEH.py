import os
import sys
import traci
import math
from enum import Enum
from Vehicle import Vehicle


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

	def update_location(self, new_location):
		super().update_location(new_location)
		self.update_state()

	def update_state(self):
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

	def show_info(self):
		print("Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))