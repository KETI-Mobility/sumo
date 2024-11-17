import os
import sys
import json
import math
import traci
import traceback
from enum import Enum

# internal_edges = [":eround_0", ":eround_1", ":eround_3", ":sround_0", "sround_1", "sround_3", "nround_0", "nround_1", "nround_3", "wround_0", "wround_2", "wround_3"]

def get_next_junction_point_by_edge(edge_id):

    next_junction = traci.edge.getToJunction(edge_id)
    junction_position = traci.junction.getPosition(next_junction)
    return junction_position


def get_slow_down_junction(vehicle_id, edge_id, vehicle_position, slow_distance, stop_distance):
    junction_position = get_next_junction_point_by_edge(edge_id)
    distance = math.sqrt((vehicle_position[0] - junction_position[0])**2 + (vehicle_position[1] - junction_position[1])**2)
    # print(f"distance:{distance}")
    max_speed = traci.vehicle.getMaxSpeed(vehicle_id)
    reduced_speed = max_speed / 2
    if distance <= stop_distance:
        reduced_speed = 0
    elif distance <= slow_distance:
        speed_ratio = distance / slow_distance
        reduced_speed = reduced_speed * speed_ratio
    return reduced_speed

def shift_next_lane():
    pass

def get_current_lane(vehicle_id):
    return traci.vehicle.getLaneID(vehicle_id)

def get_lane_number(vehicle_id):
    lane_id = get_current_lane(vehicle_id)
    edge_id = traci.lane.getEdgeID(lane_id)
    # print(f"vehicle id: {vehicle_id}, lane id: {lane_id}, edge id: {edge_id}")
    return traci.edge.getLaneNumber(edge_id)



def edm_process(my_vehicle_id, edm_vehicle_id):
    new_speed = None
    try:
        lane_id = get_current_lane(my_vehicle_id)
        edge_id = traci.lane.getEdgeID(lane_id)
        edm_lane_id = get_current_lane(edm_vehicle_id)
        edm_edge_id = traci.lane.getEdgeID(edm_lane_id)
        location = traci.vehicle.getPosition(my_vehicle_id)
        # print(f"vehicle id: {my_vehicle_id}, lane id: {lane_id}, edge id: {edge_id}")
        my_lane_position = traci.vehicle.getLanePosition(my_vehicle_id)
        edm_lane_position = traci.vehicle.getLanePosition(edm_vehicle_id)
        # print(f"my_lane_position: {my_lane_position}, edm_lane_position: {edm_lane_position}")


        if(lane_id != edm_lane_id):
            ### Roundabout 예외
            if ":" in edge_id:
                # print(f"vehicle_id : {my_vehicle_id}, edge_id : {edge_id}")
                new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)

            elif edge_id != edm_edge_id:
                new_speed = get_slow_down_junction(my_vehicle_id, edge_id, location, slow_distance=200, stop_distance=5)
                if new_speed != None:
                    traci.vehicle.setSpeed(my_vehicle_id, new_speed)
                    # print(f"another lane => vehicle id : {my_vehicle_id}, set speed {new_speed}")
            elif edm_lane_position > my_lane_position:    
                new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)
                # print(f"front position => set speed {new_speed}")
            else:
                new_speed = 0
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)
        else:
            num_lanes = get_lane_number(my_vehicle_id)

            # print(f"vehicle_id : {my_vehicle_id}, my_lane_position: {my_lane_position}, edm_lane_position: {edm_lane_position}")
            # print(f"num lanes: {num_lanes}")
            if(num_lanes > 1):
                lane_index = traci.vehicle.getLaneIndex(my_vehicle_id)
                if(num_lanes > lane_index + 1):
                    traci.vehicle.changeLane(my_vehicle_id, lane_index + 1, 30)
                else :
                    traci.vehicle.changeLane(my_vehicle_id, lane_index - 1, 30)

                new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)
                # print(f"lane change")
            elif edm_lane_position > my_lane_position:    
                new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)
                # print(f"front position => set speed {new_speed}")
            else:
                new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
                traci.vehicle.setSpeed(my_vehicle_id, new_speed)
                # print(f"same lane => set speed: {new_speed}")
    except Exception as e:
        # print(traceback.format_exc())
        # print(f"except, vehicle_id : {my_vehicle_id}")
        # new_speed = traci.vehicle.getMaxSpeed(my_vehicle_id)
        # traci.vehicle.setSpeed(my_vehicle_id, new_speed)
        pass


    return new_speed