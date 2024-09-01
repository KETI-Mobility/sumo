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
# 
# On the Apple MacBook Pro M3 Pro,
# - Install the Python GUI package:
#   brew install python-tk 
# - Set the Python evnrionment on the specific directory:
#   python3 -m venv env_sumo
#   source env_sumo/bin/activate
# - Install the modules using pip on the specific environment:
#   pip install traci
#   pip install enum34
#
# - Start the SUMO simulation with the TraCI server enabled:
#  sumo-gui -c Roundabout_8_1.sumocfg --remote-port 1337
# - Start the script:
#  python Roundabout.py
#
##############################################################################

import os
import sys
import socket
import json
import traci
import math
from enum import Enum
from typing import Union, List
from Vehicle import Vehicle, T_CDA, E_CDA, C_VEH, CE_VEH, N_VEH
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
from Channel import Channel
import GlobalSim


# Add the SUMO tools directory to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare the environment variable 'SUMO_HOME'")


# Global variables for Vehicle class
rsu_location = (0, 0)
vehicles: List[Vehicle] = []
channel = Channel()


def get_vehicle_by_id(vehicle_id) -> Vehicle:
	global vehicles

	for vehicle in vehicles:
		if vehicle.vehicle_id == vehicle_id:
			# print("Step({}) Vehicle id:{}, Found".format(GlobalSim.step, vehicle_id))
			return vehicle
	# print("Step({}) No vehicle Found".format(GlobalSim.step))
	return None

def get_data(vehicle_id) -> Union[T_CDA, E_CDA, C_VEH, CE_VEH, N_VEH]:
	global vehicles, rsu_location

	vehicle_type = traci.vehicle.getTypeID(vehicle_id)
	# print("Step({}) Vehicle id:{} type: {}".format(GlobalSim.step, vehicle_id, vehicle_type))

	vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
	# print("Step({}) Vehicle id:{} speed: {}".format(GlobalSim.step, vehicle_id, vehicle_speed))
	vehicle_max_speed = traci.vehicle.getMaxSpeed(vehicle_id)
	# print("Step({}) Vehicle id:{} max speed: {}".format(GlobalSim.step, vehicle_id, vehicle_max_speed))
	vehicle_allowed_speed = traci.vehicle.getAllowedSpeed(vehicle_id)
	# print("Step({}) Vehicle id:{} allowed speed: {}".format(GlobalSim.step, vehicle_id, vehicle_allowed_speed))
	vehicle_acceleration = traci.vehicle.getAcceleration(vehicle_id)
	# print("Step({}) Vehicle id:{} acceleration: {}".format(GlobalSim.step, vehicle_id, vehicle_acceleration))
	vehicle_speed_factor = traci.vehicle.getSpeedFactor(vehicle_id)
	# print("Step({}) Vehicle id:{} speed factor: {}".format(GlobalSim.step, vehicle_id, vehicle_speed_factor))
	vehicle_speed_mode = traci.vehicle.getSpeedMode(vehicle_id)
	# print("Vehicle id:{} speed mode: {}".format(GlobalSim.step, vehicle_id, vehicle_speed_mode))

	vehicle_position = traci.vehicle.getPosition(vehicle_id)
	# print("Step({}) Vehicle id:{} position: {}".format(GlobalSim.step, vehicle_id, vehicle_position))
	vehicle_angle = traci.vehicle.getAngle(vehicle_id)
	# print("Step({}) Vehicle id:{} angle: {}".format(GlobalSim.step, vehicle_id, vehicle_angle))
	vehicle_lane = traci.vehicle.getLaneID(vehicle_id)
	# print("Step({}) Vehicle id:{} lane: {}".format(GlobalSim.step, vehicle_id, vehicle_lane))
	vehicle_edge = traci.vehicle.getRoadID(vehicle_id)
	# print("Step({}) Vehicle id:{} edge: {}".format(GlobalSim.step, vehicle_id, vehicle_edge))

	vehicle_route = traci.vehicle.getRoute(vehicle_id)
	# print("Step({}) Vehicle id:{} route: {}".format(GlobalSim.step, vehicle_id, vehicle_route))
	vehicle_route_index = traci.vehicle.getRouteIndex(vehicle_id)
	# print("Step({}) Vehicle id:{} route index: {}".format(GlobalSim.step, vehicle_id, vehicle_route_index))

	vehicle_color = traci.vehicle.getColor(vehicle_id)
	# print("Step({}) Vehicle id:{} color: {}".format(GlobalSim.step, vehicle_id, vehicle_color))
	vehicle_length = traci.vehicle.getLength(vehicle_id)
	# print("Step({}) Vehicle id:{} length: {}".format(GlobalSim.step, vehicle_id, vehicle_length))
	vehicle_width = traci.vehicle.getWidth(vehicle_id)
	# print("Step({}) Vehicle id:{} width: {}".format(GlobalSim.step, vehicle_id, vehicle_width))
		
	vehicle_stop = traci.vehicle.getStopState(vehicle_id)
	# print("Step({}) Vehicle id:{} stop: {}".format(GlobalSim.step, vehicle_id, vehicle_stop))
	vehicle_stop_state = traci.vehicle.getStopState(vehicle_id)
	# print("Step({}) Vehicle id:{} stop state: {}".format(GlobalSim.step, vehicle_id, vehicle_stop_state))
		
	vehicle_waiting_time = traci.vehicle.getWaitingTime(vehicle_id)
	# print("Step({}) Vehicle id:{} waiting time: {}".format(GlobalSim.step, vehicle_id, vehicle_waiting_time))
	vehicle_accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
	# print("Step({}) Vehicle id:{} accumulated waiting time: {}".format(GlobalSim.step, vehicle_id, vehicle_accumulated_waiting_time))
		
	# vehicle_co2_emission = traci.vehicle.getCO2Emission(vehicle_id)
	# print("Step({}) Vehicle id:{} CO2 emission: {}".format(GlobalSim.step, vehicle_id, vehicle_co2_emission))
	# vehicle_co_emission = traci.vehicle.getCOEmission(vehicle_id)
	# print("Step({}) Vehicle id:{} CO emission: {}".format(GlobalSim.step, vehicle_id, vehicle_co_emission))
	# vehicle_hc_emission = traci.vehicle.getHCEmission(vehicle_id)
	# print("Step({}) Vehicle id:{} HC emission: {}".format(GlobalSim.step, vehicle_id, vehicle_hc_emission))
	# vehicle_pm_x_emission = traci.vehicle.getPMxEmission(vehicle_id)
	# print("Step({}) Vehicle id:{} PMx emission: {}".format(GlobalSim.step, vehicle_id, vehicle_pm_x_emission))
	# vehicle_nox_emission = traci.vehicle.getNOxEmission(vehicle_id)
	# print("Step({}) Vehicle id:{} NOx emission: {}".format(GlobalSim.step, vehicle_id, vehicle_nox_emission))
	# vehicle_fuel_consumption = traci.vehicle.getFuelConsumption(vehicle_id)
	# print("Step({}) Vehicle id:{} fuel consumption: {}".format(GlobalSim.step, vehicle_id, vehicle_fuel_consumption))

	# Search the vehicle_id in vehicles
	the_vehicle = get_vehicle_by_id(vehicle_id)
	if the_vehicle is None:
		if vehicle_type == "C-VEH":
			the_vehicle = C_VEH(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position)
		elif vehicle_type == "CE-VEH":
			the_vehicle = CE_VEH(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position)
		elif vehicle_type == "T-CDA":
			the_vehicle = T_CDA(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_route)
		elif vehicle_type == "E-CDA":
			the_vehicle = E_CDA(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_route)
		elif vehicle_type == "N-VEH":
			the_vehicle = N_VEH(GlobalSim.step, vehicle_id, vehicle_type)
		else:
			# print("Step({}) Vehicle id:{}, type:{} type not found".format(GlobalSim.step, vehicle_id, vehicle_type))
			return None
		
		# Add the vehicle to the vehicles list
		vehicles.append(the_vehicle)
		# print("Step({}) Vehicle id:{} added to the list".format(GlobalSim.step, vehicle_id))
	else:
		# Update the location of the vehicle
		if vehicle_type == "C-VEH" and vehicle_type == "CE_VEH":
			the_vehicle.update(vehicle_position, vehicle_speed)
		elif vehicle_type == "T-CDA" and vehicle_type == "E-CDA":
			the_vehicle.update(vehicle_position, vehicle_speed, vehicle_acceleration, vehicle_lane, vehicle_route)
			
		# print("Step({}) Vehicle id:{} updated".format(GlobalSim.step, vehicle_id))
		# the_vehicle.show_info()

	return the_vehicle

def send_vehicle_info(vehicle: Vehicle, udp_ip: str, udp_port: int):
	# Convert the Vehicle instance to a dictionary and then to a JSON string
	vehicle_info_json = json.dumps(vehicle.to_dict())

	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Send the JSON data through the UDP socket
	sock.sendto(vehicle_info_json.encode('utf-8'), (udp_ip, udp_port))

	# Close the socket
	sock.close()

def send_all_vehicles_info(vehicles: List[Vehicle], udp_ip: str, udp_port: int):
	for vehicle in vehicles:
		send_vehicle_info(vehicle, udp_ip, udp_port)


def custom_code_at_step() -> None:
	global vehicles

	# Add your custom code here
	vehicle_ids = traci.vehicle.getIDList()
	# print("Step({}) Vehicle IDs at step :{}".format(GlobalSim.step, vehicle_ids))

	# vehicle_id로 차량의 정보를 가져와서 the_vehicle로 반환
	# vehicles 리스트 아네 the_vehicle이 없으면 추가
	# the_vehicle의 BSM을 channel로 전송
	for vehicle_id in vehicle_ids:
		the_vehicle = get_data(vehicle_id)

		the_vehicle.update_state(GlobalSim.step)

		# C-VEH sends its own information(BSM) to E-CDA and T-CDA
		# CE-VEH sends its own information(BSM, EDM) to E-CDA and T-CDA 
		# T-CDA sends its own information(BSM+, DMM, DNM) to E-CDA
		# Then,
		# E-CDA knows the information of all vehicles (C-VEH's BSM, CE-VEH's BSM, EDM, T-CDA's BSM+, DMM, DNM)
		# T-CDA knows the information of all vehicles (C-VEH's BSM, CE-VEH's BSM, EDM, E-CDA's BSM+, DMM, DNM)
		if the_vehicle is not None and the_vehicle is not N_VEH:
			the_vehicle.send_bsm(GlobalSim.step, channel)

			# print("Type: {}".format(the_vehicle.vehicle_type))
			if the_vehicle.vehicle_type == "CE-VEH":
				the_vehicle.send_edm(GlobalSim.step, channel)

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

	# Receive the BSM from the vehicles via channel
	for the_vehicle in vehicles:
		the_vehicle.receive(GlobalSim.step, channel)

		if the_vehicle is C_VEH and the_vehicle.new_event == True:
			print(f"New event(Id: {the_vehicle.vehicle_id}): max speed: {the_vehicle.max_speed}")
			traci.vehicle.setMaxSpeed(vehicle_id, the_vehicle.max_speed)


	channel.reset()


	# Remove all vehicles from the list
	for the_vehicle in vehicles:
		if the_vehicle.stay == False:
			# print("Step({}) Vehicle id:{}, the vehicle should be removed".format(GlobalSim.step, the_vehicle.vehicle_id))
			# print("Step({}) time_birth:{}, time_exit:{}, time_life:{}".format(GlobalSim.step, the_vehicle.time_birth, GlobalSim.step, GlobalSim.step - the_vehicle.time_birth))

			vehicles.remove(the_vehicle)

	# Reset the stay flag
	for the_vehicle in vehicles:
		the_vehicle.stay = False

	# Send all vehicle information via UDP
	UDP_IP = "127.0.0.1"
	UDP_PORT = 12345
	send_all_vehicles_info(vehicles, UDP_IP, UDP_PORT)



def run_simulation() -> None:
	# Start the SUMO simulation
	#traci.start(["sumo-gui", "-c", "~/sumo/sim/coautodrv/Roundabout_8_1.sumocfg", "--remote-port", "1337"])

	# Connect to the SUMO simulation on the specified port
	traci.init(1337)

	while True: #traci.simulation.getMinExpectedNumber() > 0:
		traci.simulationStep()  # Advance the simulation by one step
		custom_code_at_step()  # Call your custom code
		GlobalSim.step += 1
		
	traci.close()

if __name__ == "__main__":
	run_simulation()
