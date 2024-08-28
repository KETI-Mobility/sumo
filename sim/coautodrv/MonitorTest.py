import tkinter as tk
import socket
import json
import random

# Vehicle class for generating JSON data
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

def send_vehicle_data():
	# Generate random vehicle data
	vehicle_id = random.randint(1, 100)
	speed = random.randint(0, 120)
	location = f"{random.uniform(-90, 90):.6f}, {random.uniform(-180, 180):.6f}"
	vehicle = Vehicle(vehicle_id, speed, location)

	# Serialize vehicle data to JSON
	json_data = vehicle.to_json()
	json_bytes = json_data.encode('utf-8')

	# Prepare TLV formatted data
	type_field = 1  # Assuming 1 is the type for JSON data
	length_field = len(json_bytes)
	tlv_data = bytes([type_field, length_field]) + json_bytes

	# Send TLV data via UDP
	sock.sendto(tlv_data, (UDP_IP, UDP_PORT))
	status_label.config(text=f"Sent: {json_data}")

def create_gui():
	global status_label

	# Set up the main window
	root = tk.Tk()
	root.title("JSON Vehicle Data Sender")
	root.geometry("400x200")

	# Create and pack the widgets
	send_button = tk.Button(root, text="Send Vehicle Data", command=send_vehicle_data)
	send_button.pack(pady=20)

	status_label = tk.Label(root, text="")
	status_label.pack(pady=20)

	# Start the Tkinter event loop
	root.mainloop()

if __name__ == "__main__":
	# UDP configuration
	UDP_IP = "127.0.0.1"  # Localhost (adjust if needed)
	UDP_PORT = 12345  # Port to send to (same as the receiver program)

	# Create a UDP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Create the GUI
	create_gui()
