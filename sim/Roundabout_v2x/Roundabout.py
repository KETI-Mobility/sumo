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
#  sumo-gui -c sumocfg/Roundabout_D_8_1_rsu_case2.sumocfg --remote-port 1337
#  sumo-gui -c sumocfg/Roundabout_D_8_1_rsu_case3.sumocfg --remote-port 1337
#  sumo-gui -c sumocfg/Roundabout_D_8_1_rsu.sumocfg --remote-port 1337
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

import traci.domain
from Vehicle import Vehicle, T_CDA, E_CDA, C_VEH, CE_VEH, N_VEH
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
from Channel import Channel, RSU
import GlobalSim


# Add the SUMO tools directory to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare the environment variable 'SUMO_HOME'")


# Global variables for Vehicle class
rsu_location = (0, 0)
vehicles = {}
channel = Channel()
rsu = RSU(rsu_location, 1000)
min_gap = 0.0
tau = 0.0
mode = 0
ENABLE = True

# Constants
CLASS_A = 0
CLASS_B = 1
CLASS_C = 2
CLASS_D = 3
SIM_CLASS = CLASS_D


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
	# print("Vehicle id:{} speed mode: {}".format(GlobalSim.step, vehicle_speed_mode))

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
	# the_vehicle = get_vehicle_by_id(vehicle_id)
	the_vehicle = vehicles.get(vehicle_id)
	if the_vehicle is None:
		if vehicle_type[:5] == "C-VEH":
			the_vehicle = C_VEH(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_route, (vehicle_length, vehicle_width), vehicle_edge, vehicle_route_index)
		elif vehicle_type[:6] == "CE-VEH":
			the_vehicle = CE_VEH(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_route, (vehicle_length, vehicle_width), vehicle_edge, vehicle_route_index)
			traci.vehicle.setSpeedMode(vehicle_id, 55)
		elif vehicle_type[:5] == "T-CDA":
			the_vehicle = T_CDA(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_edge, vehicle_route, (vehicle_length, vehicle_width))
		elif vehicle_type[:5] == "E-CDA":
			the_vehicle = E_CDA(GlobalSim.step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_position, vehicle_acceleration, vehicle_lane, vehicle_edge, vehicle_route, (vehicle_length, vehicle_width))
		elif vehicle_type[:5] == "N-VEH":
			the_vehicle = N_VEH(GlobalSim.step, vehicle_id, vehicle_type)
		else:
			print(f"Step({GlobalSim.step}) {vehicle_id}, type: {vehicle_type} is not supported")
			return None
		
		# Add the vehicle to the vehicles list
		vehicles[vehicle_id] = the_vehicle
		# print(f"Step({GlobalSim.step}) {the_vehicle.vehicle_id} is the new vehicle")
	else:
		# Update the location of the vehicle
		if vehicle_type[:5] == "C-VEH" or vehicle_type[:6] == "CE-VEH":
			the_vehicle.update(vehicle_position, vehicle_speed, vehicle_acceleration, vehicle_lane, vehicle_route, vehicle_edge, vehicle_route_index, vehicle_accumulated_waiting_time)
		elif vehicle_type[:5] == "T-CDA" or vehicle_type[:5] == "E-CDA":
			the_vehicle.update(vehicle_position, vehicle_speed, vehicle_acceleration, vehicle_lane, vehicle_edge, vehicle_route)
			
		# print(f"Step({GlobalSim.step}) {the_vehicle.vehicle_id} is updated")
		
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

def send_all_vehicles_info(vehicles, udp_ip: str, udp_port: int):
	for vehicle_id in vehicles:
		v = vehicles[vehicle_id]

		send_vehicle_info(v, udp_ip, udp_port)


# Roundabout (Class D)
# CE-VEH broadcasts EDM 
# E-CDA determines pass or yield to CE-VEH
def custom_code_at_step_class_rsu() -> None:
	global vehicles, min_gap, tau, mode

	# Add your custom code here
	vehicle_ids = traci.vehicle.getIDList()
	# print("Step({}) Vehicle IDs at step :{}".format(GlobalSim.step, vehicle_ids))

	# vehicle_id로 차량의 정보를 가져와서 the_vehicle로 반환
	# vehicles 리스트에 the_vehicle이 없으면 추가
	# the_vehicle의 BSM을 channel로 전송
	for vehicle_id in vehicle_ids:
		the_vehicle = get_data(vehicle_id)

		the_vehicle.update_state(GlobalSim.step)

		if the_vehicle is not None and the_vehicle is not N_VEH:
			# the_vehicle.send_bsm(GlobalSim.step, rsu)
			pass

			# print("Type: {}".format(the_vehicle.vehicle_type))
			if the_vehicle.vehicle_type == "CE-VEH":
				# print(f"Step({GlobalSim.step}) {the_vehicle.vehicle_id} send EDM")
				the_vehicle.send_edm(GlobalSim.step, rsu)

	for vehicle_id in vehicles:
		v = vehicles[vehicle_id]
		v.receive(GlobalSim.step, rsu)
		
		if ENABLE == True:	# True/False로 시뮬레이션 하기
			if v.vehicle_type == "C-VEH" and v.new_event == True:
				# traci.lane.setDisallowed("NW_0", C_VEH)
				traci.vehicle.setSpeed(v.vehicle_id, v.max_speed)
			
				v.new_event = False
		
	rsu.reset()


	# Remove the vehicle from vehicles if stay is False
	list_vehicles_to_remove = []
	for vehicle_id in vehicles:
		v = vehicles[vehicle_id]
		if v.stay == False:
			if v.vehicle_type == "CE-VEH":
				print(f"Step({GlobalSim.step - v.time_birth}) {v.vehicle_id} is arrived")
				print(f"accumulated waiting time :{v.vehicle_accum_wait_time}")
			list_vehicles_to_remove.append(vehicle_id)
	
	for id in list_vehicles_to_remove:
		# print(f"Step({GlobalSim.step}) {id} is removed")
		del vehicles[id]
	
	# Reset the stay flag
	for vehicle_id in vehicles:
		v = vehicles[vehicle_id]
		v.stay = False
		
	# Send all vehicle information via UDP
	UDP_IP = "127.0.0.1"
	UDP_PORT = 12345
	send_all_vehicles_info(vehicles, UDP_IP, UDP_PORT)



def run_simulation() -> None:
	# Start the SUMO simulation
	# traci.start(["sumo-gui", "-c", "~/sumo/sim/coautodrv/Roundabout_8_1.sumocfg", "--remote-port", "1337"])

	is_visible = 0
	# Connect to the SUMO simulation on the specified port
	traci.init(1337)
	
	while True: #traci.simulation.getMinExpectedNumber() > 0:
		traci.simulationStep()  # Advance the simulation by one step
		custom_code_at_step_class_rsu()
		GlobalSim.step += 1
		if is_visible == 0:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 1
		elif is_visible == 1:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,255))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 2
		elif is_visible == 2:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,255))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 3
		elif is_visible == 3:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,255))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 4
		elif is_visible == 4:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,255))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 5
		elif is_visible == 5:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,255))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 6
		elif is_visible == 6:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,255))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 7
		elif is_visible == 7:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,255))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 8
		elif is_visible == 8:
			traci.polygon.setColor("antenna_area_50", (255,0,0,0))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,255))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 9
		elif is_visible == 9:
			traci.polygon.setColor("antenna_area_50", (255,0,0,255))
			traci.polygon.setColor("antenna_area_100", (255,0,0,0))
			traci.polygon.setColor("antenna_area_200", (255,0,0,0))
			traci.polygon.setColor("antenna_area_300", (255,0,0,0))
			traci.polygon.setColor("antenna_area_400", (255,0,0,0))
			traci.polygon.setColor("antenna_area_500", (255,0,0,0))
			traci.polygon.setColor("antenna_area_600", (255,0,0,0))
			traci.polygon.setColor("antenna_area_700", (255,0,0,0))
			traci.polygon.setColor("antenna_area_800", (255,0,0,0))
			is_visible = 1
		
	traci.close()

if __name__ == "__main__":
	run_simulation()
