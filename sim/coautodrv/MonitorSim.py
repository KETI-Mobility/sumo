import sys
import json
import socket
import threading
import tkinter as tk
from tkinter import ttk


# Vehicle class to handle JSON serialization and deserialization
class Vehicle:
	def __init__(self, vehicle_id, speed, location):
		self.id = vehicle_id
		self.speed = speed
		self.location = location

	def to_json(self):
		return json.dumps({
			"id": self.id,
			"speed": self.speed,
			"location": self.location
		})

	@staticmethod
	def from_json(data):
		obj = json.loads(data)
		return Vehicle(obj['id'], obj['speed'], obj['location'])


# Thread function to handle UDP socket communication
def udp_receiver_thread(vehicles, update_callback, port, stop_event):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))

	while not stop_event.is_set():
		try:
			data, _ = sock.recvfrom(1024)  # Buffer size is 1024 bytes
			print("Rx data:", data)
			
			if data:
				# Assuming data is TLV formatted
				type_field = data[0]
				length_field = data[1]
				if type_field == 1:  # T=1 for JSON
					json_data = data[2:2 + length_field].decode('utf-8')
					vehicle = Vehicle.from_json(json_data)

					# Update vehicle list in GUI
					update_callback(vehicles, vehicle)
		except Exception as e:
			print(f"Error processing data: {e}")
			break

	sock.close()


# Function to update vehicle list in the GUI
def update_vehicle_list(vehicles, vehicle):
	if vehicle.id in vehicles:
		# Update existing vehicle info
		vehicles[vehicle.id] = vehicle
	else:
		# Add new vehicle
		vehicles[vehicle.id] = vehicle

	refresh_vehicle_list(vehicles)


# Function to refresh the GUI vehicle list
def refresh_vehicle_list(vehicles):
	for row in tree.get_children():
		tree.delete(row)

	for vehicle_id, vehicle in vehicles.items():
		tree.insert("", "end", values=(vehicle.id, vehicle.speed, vehicle.location))


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
	global tree, port_entry, toggle_button, status_label
	global vehicles, server_running, udp_thread, stop_event

	vehicles = {}  # Dictionary to store vehicle objects
	server_running = False  # Server running state
	stop_event = threading.Event()  # Event to stop the server thread

	# Create main window
	root = tk.Tk()
	root.title("Vehicle Monitor")
	root.geometry("500x400")

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
	columns = ("ID", "Speed", "Location")
	tree = ttk.Treeview(root, columns=columns, show="headings")
	tree.heading("ID", text="ID")
	tree.heading("Speed", text="Speed")
	tree.heading("Location", text="Location")
	tree.pack(fill=tk.BOTH, expand=True, pady=20)

	# Start Tkinter event loop
	root.mainloop()


if __name__ == "__main__":
	main()
