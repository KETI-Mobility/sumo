import os
import sys
import traci
import math
from enum import Enum
from typing import List
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
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
		print("Step({}) V2X: Messages: {}".format(GlobalSim.step, len(self.messages)))

