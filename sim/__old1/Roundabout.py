#!/usr/bin/env python

# [IMPORTANT INFO]
# How to add new vehicle's parameter
# https://sumo.dlr.de/docs/Developer/How_To/Extend_Vehicles.html

import os
import sys
import optparse

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("Please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary # Checks for the binary in environ vars
import traci    
# /usr/local/lib/libsumocpp.so, /usr/local/lib/libtracicpp.so
# /usr/local/lib/python3.8/dist-packages/libsumo
# /usr/local/lib/python3.8/dist-packages/libtraci
# /usr/local/lib/python3.8/dist-packagessumolib
# /usr/local/lib/python3.8/dist-packages/traci


def get_options():
	opt_parse = optparse.OptionParser()
	opt_parse.add_option("--nogui", action="store_true", default=False, help="run the commandline version of sumo")

	options, args = opt_parse.parse_args()
	return options

def get_distance(pos1, pos2):
	dist = ((pos1[0] - pos2[0]) ** 2) + ((pos1[1] - pos2[1]) ** 2)
	dist = dist ** 0.5
	return dist


# contains TraCI control loop
def run():
	vip_is_on_road = False

	step = 0
	while traci.simulation.getMinExpectedNumber() > 0:
		traci.simulationStep()

		# print("Setp", step)
		id = ""
		ids = traci.vehicle.getIDList()
		# print(ids)

		# To check whether VIP is 
		is_vip = False
		for id in ids:
			# print(id)

			if id[:5] == "f_vip":
				lane_id = traci.vehicle.getLaneID(vehID=id)
				if lane_id[:3] == "-E3" or lane_id[:3] == "E13":
					is_vip = True

		# To confirm whether VIP's status
		if not vip_is_on_road:
			if not is_vip:
				pass
				# print("No VIP yet!")
			else:
				vip_is_on_road = True
				print("VIP is coming!")
		else:
			if is_vip:
				pass
				# print("VIP is on road!")
			else:
				vip_is_on_road = False
				print("VIP left!")

		# To act 
		try:
			for id in ids:
				if id[:5] != "f_vip":
					lane_id = traci.vehicle.getLaneID(vehID=id)
					# print("VehclieID={0}, speed = {1} m/s, LaneID={2}".format(id, str(traci.vehicle.getSpeed(vehID=id)), lane_id))

					if vip_is_on_road:
						if lane_id[:3] == "-E2" or traci.vehicle.getParameter(id, "SlowDown") != "1":
							# Calculate the vehicle's distance from the junction.
							pos_j = traci.junction.getPosition("J12")
							pos_v = traci.vehicle.getPosition(id)
							dist = get_distance(pos_j, pos_v)
							print("{0}'s distance: {1}".format(id, dist))

							if dist < 50:
								traci.vehicle.setParameter(id, "SlowDown", "1")

								print("{0}'s Slow speed!".format(id))
								traci.vehicle.slowDown(vehID=id, speed=0, duration=10)

							# traci.vehicle.setSpeed(vehID=id, speed=0) <== it's working
							# traci.vehicle.setMaxSpeed(vehID=id, speed=0) <== it's not working
							# print("{0}'s Speed mode = {1}".format(id, traci.vehicle.getSpeedMode(vehID=id))) <== SpeedMode doesn't change
						else:
							pass
					else:
						# VIP disappears
						if traci.vehicle.getParameter(id, "SlowDown") == "1":
							print("{0}'s vehicle's speed is recovered.".format(id))

							traci.vehicle.setParameter(id, "SlowDown", "0")
							traci.vehicle.setSpeed(vehID=id, speed=traci.vehicle.getMaxSpeed(typeID=id))

		except Exception as err:
			print("An exception occurred", err)

		# print(traci.vehicle.getTypeID(vehID="f_r0.0")) # return 't_bus'
		# print(type(traci.vehicle))  # traci.vehicle is 'traci._vehicle.VehicleDomain'
	
		step += 1

	traci.close()
	sys.stdout.flush()

# main entry point
if __name__ == "__main__":
	options = get_options()

	#check binary
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')

	# traci starts sumo as a subprocess and then this script connects and runs
	traci.start([sumoBinary, "-c", "Roundabout.sumocfg", "--tripinfo-output", "tripinfo.xml"])

	run()