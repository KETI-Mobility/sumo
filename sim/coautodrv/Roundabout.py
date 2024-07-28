import os
import sys

# Add the SUMO tools directory to the PYTHONPATH
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare the environment variable 'SUMO_HOME'")


import traci

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
		
		vehicle_co2_emission = traci.vehicle.getCO2Emission(vehicle_id)
		print("Vehicle {} CO2 emission: {}".format(vehicle_id, vehicle_co2_emission))
		vehicle_co_emission = traci.vehicle.getCOEmission(vehicle_id)
		print("Vehicle {} CO emission: {}".format(vehicle_id, vehicle_co_emission))
		vehicle_hc_emission = traci.vehicle.getHCEmission(vehicle_id)
		print("Vehicle {} HC emission: {}".format(vehicle_id, vehicle_hc_emission))
		vehicle_pm_x_emission = traci.vehicle.getPMxEmission(vehicle_id)
		print("Vehicle {} PMx emission: {}".format(vehicle_id, vehicle_pm_x_emission))
		vehicle_nox_emission = traci.vehicle.getNOxEmission(vehicle_id)
		print("Vehicle {} NOx emission: {}".format(vehicle_id, vehicle_nox_emission))
		vehicle_fuel_consumption = traci.vehicle.getFuelConsumption(vehicle_id)
		print("Vehicle {} fuel consumption: {}".format(vehicle_id, vehicle_fuel_consumption))
		
		
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
