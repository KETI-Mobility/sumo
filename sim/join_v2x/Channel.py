import os
import sys
import traci
import math
from enum import Enum
from typing import List
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp, DetectMessage
import GlobalSim

class Channel:
	def __init__(self):
		self.messages: List[Message] = []

	def reset(self) -> None:
		# Reset the channel
		self.messages.clear()
	
	def add_message(self, message:Message) -> None:
		# Add a message to the channel
		self.messages.append(message)	

	def show_info(self) -> None:
		pass
		# print("Step({}) V2X: Messages: {}".format(GlobalSim.step, len(self.messages)))


class RSU(Channel):
	def __init__(self, rsu_location, range):
		super().__init__()
		self.rsu_location = rsu_location
		self.range = range
	
	def add_message(self, message: Message) -> None:
		if isinstance(message, BSM) or isinstance(message, BSMplus) or isinstance(message, EDM) or isinstance(message, DMM) or isinstance(message, DNMReq) or isinstance(message, DNMResp):
			if math.sqrt((self.rsu_location[0] - message.sender_location[0])**2 + (self.rsu_location[1] - message.sender_location[1])**2) < self.range:
				return super().add_message(message)
		if isinstance(message, DetectMessage):
			return super().add_message(message)