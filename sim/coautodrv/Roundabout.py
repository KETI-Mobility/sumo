##############################################################################
# This script is a template for custom code that can be executed during the
# simulation. The script is executed at each simulation step and can be used
# to interact with the simulation, e.g., to retrieve information about the
# vehicles, the environment, etc.
#
# The script is executed in the context of the SUMO simulation, i.e., it has
# access to the simulation state and can interact with the simulation using
# the TraCI API.
#
# The script can be used to implement custom logic, e.g., to control the
# vehicles, to collect data, to visualize the simulation, etc.
#
# Usage:
# - Start the SUMO simulation with the TraCI server enabled:
#  sumo-gui -c Roundabout_8_1.sumocfg --remote-port 1337
# - Start the script:
#  python Roundabout.py
#
##############################################################################

import os
import sys

# Add the SUMO tools directory to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare the environment variable 'SUMO_HOME'")


import os
import sys
import traci
import math
from enum import Enum

class VehicleState(Enum):
	INITIAL = 1
	ADDED = 2
	APPROACHING = 3
	INSIDE = 4
	EXITING = 5
	REMOVED = 6

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
		self.state = VehicleState.INITIAL

	def update_location(self, new_location):
		self.cur_location = new_location
		self.update_state()

	def update_state(self):
		if self.state == VehicleState.INITIAL:
			print("INITIAL -> ADDED")
			self.state = VehicleState.ADDED
		elif self.state == VehicleState.ADDED and self.get_distance(self) < 100:
			print("ADDED -> APPROACHING")
			self.state = VehicleState.APPROACHING
		elif self.state == VehicleState.APPROACHING and self.get_distance(self) < 50:
			print("APPROACHING -> INSIDE")
			self.state = VehicleState.INSIDE
		elif self.state == VehicleState.INSIDE and self.get_distance(self) > 50:
			print("INSIDE -> EXITING")
			self.state = VehicleState.EXITING
		elif self.state == VehicleState.EXITING and self.get_distance(self) > 100:
			print("EXITING -> REMOVED")
			self.state = VehicleState.REMOVED

	def get_distance(self):
		self.distance = math.sqrt((self.x_location[0] - self.cur_location[0])**2 + (self.x_location[1] - self.cur_location[1])**2)
		return self.distance
	
	def print(self):
		print("Vehicle ID: {}, Type: {}, State: {}, Distance: {}".format(self.vehicle_id, self.vehicle_type, self.state, self.distance))




# Global variables for Vehicle class
vehicles = []


def get_vehicle_by_id(vehicle_id, vehicles):
	for vehicle in vehicles:
		if vehicle.vehicle_id == vehicle_id:
			print("Found, vehicle ID: {}".format(vehicle_id))
			return vehicle
	print("None")
	return None

def custom_code_at_step(step):
	# Add your custom code here
	print("Simulation step: {}".format(step))
	vehicle_ids = traci.vehicle.getIDList()
	print("Vehicle IDs at step {}: {}".format(step, vehicle_ids))
	for vehicle_id in vehicle_ids:
		print("Vehicle ID: {}".format(vehicle_id))
		vehicle_type = traci.vehicle.getTypeID(vehicle_id)
		print("Vehicle {} type: {}".format(vehicle_id, vehicle_type))

		vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
		print("Vehicle {} speed: {}".format(vehicle_id, vehicle_speed))
		vehicle_max_speed = traci.vehicle.getMaxSpeed(vehicle_id)
		print("Vehicle {} max speed: {}".format(vehicle_id, vehicle_max_speed))
		vehicle_allowed_speed = traci.vehicle.getAllowedSpeed(vehicle_id)
		print("Vehicle {} allowed speed: {}".format(vehicle_id, vehicle_allowed_speed))
		vehicle_acceleration = traci.vehicle.getAcceleration(vehicle_id)
		print("Vehicle {} acceleration: {}".format(vehicle_id, vehicle_acceleration))
		vehicle_speed_factor = traci.vehicle.getSpeedFactor(vehicle_id)
		print("Vehicle {} speed factor: {}".format(vehicle_id, vehicle_speed_factor))
		vehicle_speed_mode = traci.vehicle.getSpeedMode(vehicle_id)
		print("Vehicle {} speed mode: {}".format(vehicle_id, vehicle_speed_mode))

		vehicle_position = traci.vehicle.getPosition(vehicle_id)
		print("Vehicle {} position: {}".format(vehicle_id, vehicle_position))
		vehicle_angle = traci.vehicle.getAngle(vehicle_id)
		print("Vehicle {} angle: {}".format(vehicle_id, vehicle_angle))
		vehicle_lane = traci.vehicle.getLaneID(vehicle_id)
		print("Vehicle {} lane: {}".format(vehicle_id, vehicle_lane))
		vehicle_edge = traci.vehicle.getRoadID(vehicle_id)
		print("Vehicle {} edge: {}".format(vehicle_id, vehicle_edge))

		vehicle_route = traci.vehicle.getRoute(vehicle_id)
		print("Vehicle {} route: {}".format(vehicle_id, vehicle_route))
		vehicle_route_index = traci.vehicle.getRouteIndex(vehicle_id)
		print("Vehicle {} route index: {}".format(vehicle_id, vehicle_route_index))

		vehicle_type = traci.vehicle.getTypeID(vehicle_id)
		print("Vehicle {} type: {}".format(vehicle_id, vehicle_type))
		vehicle_color = traci.vehicle.getColor(vehicle_id)
		print("Vehicle {} color: {}".format(vehicle_id, vehicle_color))
		vehicle_length = traci.vehicle.getLength(vehicle_id)
		print("Vehicle {} length: {}".format(vehicle_id, vehicle_length))
		vehicle_width = traci.vehicle.getWidth(vehicle_id)
		print("Vehicle {} width: {}".format(vehicle_id, vehicle_width))
		
		vehicle_stop = traci.vehicle.getStopState(vehicle_id)
		print("Vehicle {} stop: {}".format(vehicle_id, vehicle_stop))
		vehicle_stop_state = traci.vehicle.getStopState(vehicle_id)
		print("Vehicle {} stop state: {}".format(vehicle_id, vehicle_stop_state))
		
		vehicle_waiting_time = traci.vehicle.getWaitingTime(vehicle_id)
		print("Vehicle {} waiting time: {}".format(vehicle_id, vehicle_waiting_time))
		vehicle_accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
		print("Vehicle {} accumulated waiting time: {}".format(vehicle_id, vehicle_accumulated_waiting_time))
		
		# vehicle_co2_emission = traci.vehicle.getCO2Emission(vehicle_id)
		# print("Vehicle {} CO2 emission: {}".format(vehicle_id, vehicle_co2_emission))
		# vehicle_co_emission = traci.vehicle.getCOEmission(vehicle_id)
		# print("Vehicle {} CO emission: {}".format(vehicle_id, vehicle_co_emission))
		# vehicle_hc_emission = traci.vehicle.getHCEmission(vehicle_id)
		# print("Vehicle {} HC emission: {}".format(vehicle_id, vehicle_hc_emission))
		# vehicle_pm_x_emission = traci.vehicle.getPMxEmission(vehicle_id)
		# print("Vehicle {} PMx emission: {}".format(vehicle_id, vehicle_pm_x_emission))
		# vehicle_nox_emission = traci.vehicle.getNOxEmission(vehicle_id)
		# print("Vehicle {} NOx emission: {}".format(vehicle_id, vehicle_nox_emission))
		# vehicle_fuel_consumption = traci.vehicle.getFuelConsumption(vehicle_id)
		# print("Vehicle {} fuel consumption: {}".format(vehicle_id, vehicle_fuel_consumption))
		
		# Search the vehicle_id in vehicles
		the_vehicle = get_vehicle_by_id(vehicle_id, vehicles)
		if the_vehicle is None:
			# Add the vehicle to the vehicles list
			vehicles.append(Vehicle(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, vehicle_position))
			print("Vehicle {} added to the list".format(vehicle_id))
		else:
			# Update the location of the vehicle
			the_vehicle.update_location(vehicle_position)
			the_vehicle.print()


def run_simulation():
	# Start the SUMO simulation
	#traci.start(["sumo-gui", "-c", "~/sumo/sim/coautodrv/Roundabout_8_1.sumocfg", "--remote-port", "1337"])

	# Connect to the SUMO simulation on the specified port
	traci.init(1337)

	step = 0
	while True: #traci.simulation.getMinExpectedNumber() > 0:
		traci.simulationStep()  # Advance the simulation by one step
		custom_code_at_step(step)  # Call your custom code
		step += 1
		
	traci.close()

if __name__ == "__main__":
	run_simulation()
