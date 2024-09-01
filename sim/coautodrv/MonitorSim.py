import os
import sys
import json
import socket
import math
import json
import threading
import tkinter as tk
from tkinter import ttk
from enum import Enum
from typing import Union, List
from Vehicle import Vehicle, T_CDA, E_CDA, C_VEH, CE_VEH, N_VEH
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
from Channel import Channel

# Global variables
root = tk.Tk()
tree = None
sock = None
port_entry = None
toggle_button = None
status_label = None
vehicles = {}  # Dictionary to store vehicle objects
server_running = False  # Server running state
udp_thread = None
stop_event = None  # Event to stop the server thread
step = 0

# Thread function to handle UDP socket communication
def udp_receiver_thread(vehicles, update_callback, port, stop_event):
	global sock, step

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', port))
	except Exception as e:
		print(f"Error setting up socket: {e}")
		return

	while not stop_event.is_set():
		try:
			data, _ = sock.recvfrom(1024)  # Buffer size is 1024 bytes
			if data:
				json_data = data.decode('utf-8')
				print("Rx data:", json_data)
			
				# Parse the JSON data
				data_dict = json.loads(json_data)

				# Extract the "time_birst" value
				step = data_dict.get("time_birth")		
				vehicle_id = data_dict.get("vehicle_id")
				vehicle_type = data_dict.get("vehicle_type")
				rsu_location = data_dict.get("rsu_location")
				vehicle_speed = data_dict.get("vehicle_speed")
				vehicle_location = data_dict.get("vehicle_location")
				vehicle_acceleration = data_dict.get("vehicle_acceleration")
				vehicle_lane = data_dict.get("vehicle_lane")
				vehicle_route = data_dict.get("vehicle_route")
				state = data_dict.get("state")

				print(step, vehicle_id, vehicle_type, rsu_location, vehicle_speed, vehicle_location, vehicle_acceleration, vehicle_lane, vehicle_route, state)

				# Mapping of vehicle types to their respective classes
				vehicle_class_map = {
						"N-VEH": N_VEH,
						"C-VEH": C_VEH,
						"CE-VEH": CE_VEH,
						"T-CDA": T_CDA,
						"E-CDA": E_CDA
				}
				# Get the appropriate class based on vehicle_type
				vehicle_class = vehicle_class_map.get(vehicle_type)
				print("Vehicle Class:", vehicle_class)
				if vehicle_class:
					vehicle = vehicle_class.from_json(json_data)
					print(vehicle_class)

					# Update vehicle list in GUI
					update_callback(vehicles, vehicle)
				else:
					print(f"Unknown vehicle class: {vehicle_type}")
				
		except Exception as e:
			print(f"Error processing data: {e}")
			break

	sock.close()


# Function to update vehicle list in the GUI
def update_vehicle_list(vehicles, vehicle):
	if vehicle.vehicle_id in vehicles:
		# Update existing vehicle info
		vehicles[vehicle.vehicle_id] = vehicle
	else:
		# Add new vehicle
		vehicles[vehicle.vehicle_id] = vehicle

	refresh_vehicle_list(vehicles)


# Function to refresh the GUI vehicle list
def refresh_vehicle_list(vehicles):
	global tree, step

	for row in tree.get_children():
		tree.delete(row)

	# "Time", "V ID", "V Type", "R Location", "V Speed", "V Location", "V Acceleration", "V Lane", "V Route")
	for vehicle_id, vehicle in vehicles.items():
		if vehicle.vehicle_type == "N-VEH":
			tree.insert("", "end", values=(step, vehicle.vehicle_id, vehicle.vehicle_type))
		elif vehicle.vehicle_type == "C-VEH":
			tree.insert("", "end", values=(step, vehicle.vehicle_id, vehicle.vehicle_type, vehicle.rsu_location, vehicle.vehicle_speed, vehicle.vehicle_location))
		elif vehicle.vehicle_type == "CE-VEH":
			tree.insert("", "end", values=(step, vehicle.vehicle_id, vehicle.vehicle_type, vehicle.rsu_location, vehicle.vehicle_speed, vehicle.vehicle_location))
		elif vehicle.vehicle_type == "T-CDA":
			tree.insert("", "end", values=(step, vehicle.vehicle_id, vehicle.vehicle_type, vehicle.rsu_location, vehicle.vehicle_speed, vehicle.vehicle_location, vehicle.vehicle_acceleration, vehicle.vehicle_lane, vehicle.vehicle_route))
		elif vehicle.vehicle_type == "E-CDA":
			tree.insert("", "end", values=(step, vehicle.vehicle_id, vehicle.vehicle_type, vehicle.rsu_location, vehicle.vehicle_speed, vehicle.vehicle_location, vehicle.vehicle_acceleration, vehicle.vehicle_lane, vehicle.vehicle_route))
		else:
			print(f"Unknown vehicle type: {vehicle.vehicle_type}")

# Start or stop the server based on the button click
def toggle_server():
	global udp_thread, stop_event, server_running

	if server_running:
		# Stop the server
		stop_event.set()
		udp_thread.join()
		toggle_button.config(text="Start")
		server_running = False
	else:
		# Start the server
		try:
			port = int(port_entry.get())
			stop_event.clear()
			udp_thread = threading.Thread(target=udp_receiver_thread, args=(vehicles, update_vehicle_list, port, stop_event))
			udp_thread.daemon = True
			udp_thread.start()
			toggle_button.config(text="Stop")
			server_running = True
		except ValueError:
			status_label.config(text="Invalid port number")

# Main function to create the GUI
def main():
	global root, tree, port_entry, toggle_button, status_label
	global vehicles, server_running, udp_thread, stop_event

	vehicles = {}  # Dictionary to store vehicle objects
	server_running = False  # Server running state
	stop_event = threading.Event()  # Event to stop the server thread

	# Create main window
	root.title("Vehicle Monitor")
	root.geometry("900x500")

	# Frame for port entry and control button
	control_frame = tk.Frame(root)
	control_frame.pack(pady=10)

	tk.Label(control_frame, text="Port:").pack(side=tk.LEFT)
	port_entry = tk.Entry(control_frame)
	port_entry.pack(side=tk.LEFT, padx=5)
	port_entry.insert(0, "12345")  # Default port

	toggle_button = tk.Button(control_frame, text="Start", command=toggle_server)
	toggle_button.pack(side=tk.LEFT, padx=5)

	status_label = tk.Label(root, text="")
	status_label.pack(pady=10)

	# Treeview for displaying vehicles
	columns = ("Time", "V ID", "V Type", "R Location", "V Speed", "V Location", "V Acceleration", "V Lane", "V Route")
	tree = ttk.Treeview(root, columns=columns, show="headings")
	tree.heading("Time", text="Time")
	tree.heading("V ID", text="V ID")
	tree.heading("V Type", text="V Type")
	tree.heading("R Location", text="R Location")
	tree.heading("V Speed", text="V Speed")
	tree.heading("V Location", text="V Location")
	tree.heading("V Acceleration", text="V Acceleration")
	tree.heading("V Lane", text="V Lane")
	tree.heading("V Route", text="V Route")

	# Customize column widths
	tree.column("Time", width=60)
	tree.column("V ID", width=80)
	tree.column("V Type", width=80)
	tree.column("R Location", width=120)
	tree.column("V Speed", width=80)
	tree.column("V Location", width=120)
	tree.column("V Acceleration", width=80)
	tree.column("V Lane", width=60)
	tree.column("V Route", width=200)

	tree.pack(fill=tk.BOTH, expand=True, pady=20)

	# Start Tkinter event loop
	root.mainloop()


if __name__ == "__main__":
	main()
