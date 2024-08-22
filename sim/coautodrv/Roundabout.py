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
# ImportError: No module named enum
# - Install the enum module using pip:
#   pip install enum34
##############################################################################

import os
import sys
import traci
import math
from enum import Enum
from Vehicle import Vehicle
from Vehicle_T_CDA import T_CDA
from Vehicle_C_VEH import C_VEH
from Vehicle_CE_VEH import CE_VEH
from Vehicle_E_CDA import E_CDA


# Add the SUMO tools directory to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare the environment variable 'SUMO_HOME'")


# Global variables for Vehicle class
vehicles = []
shared_data = []

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
			if vehicle_type == "T_CDA":
				the_vehicle = T_CDA(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, vehicle_position)
			elif vehicle_type == "C_VEH":
				the_vehicle = C_VEH(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, vehicle_position)
			elif vehicle_type == "CE_VEH":
				the_vehicle = CE_VEH(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, vehicle_position)
			elif vehicle_type == "E_CDA":
				the_vehicle = E_CDA(vehicle_id, vehicle_type, vehicle_color, vehicle_length, vehicle_width, vehicle_position)
			else:
				print("Vehicle {} type not found".format(vehicle_id))
				return
			
			# Add the vehicle to the vehicles list
			vehicles.append(the_vehicle)
			print("Vehicle {} added to the list".format(vehicle_id))
		else:
			# Update the location of the vehicle
			the_vehicle.update_location(vehicle_position)
			the_vehicle.show_info()

		# C-VEH sends its own information(BSM) to E-CDA and T-CDA
		# CE-VEH sends its own information(BSM, EDM) to E-CDA and T-CDA 
		# T-CDA sends its own information(BSM+, DMM, DNM) to E-CDA
		# Then,
		# E-CDA knows the information of all vehicles (C-VEH's BSM, CE-VEH's BSM, EDM, T-CDA's BSM+, DMM, DNM)
		# T-CDA knows the information of all vehicles (C-VEH's BSM, CE-VEH's BSM, EDM, E-CDA's BSM+, DMM, DNM)

		# Roundabout (Class A)
		# E-CDA evaulates C-VEH's existence on roundabout (to check C-VEH's speed, TTB(Time-to-Break) at cross point)
		# Scenario A-8-1: E-CDA passes through the roundabout without yielding to C-VEH
		# Scenario A-8-2: E-CDA yields to C-VEH

		# Roundabout (Class B)
		# E-CDA evaluates T-CDA's manuever.Exit_Loc with E-CDA's path
		# Scenario B-8-1: E-CDA passes through the roundabout without yielding to T-CDA
		# Scenario B-8-2: E-CDA yields to T-CDA

		# Roundabout (Class C)
		# Negotiation between E-CDA and T-CDA while exchaning Req, Resp, DNM between E-CDA and T-CDA

		# Roundabout (Class D)
		# CE-VEH broadcasts EDM 
		# E-CDA determines pass or yield to CE-VEH




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
