import os
import sys
import traci
import math
from enum import Enum
from Message import *
from Vehicle import *


class Channel:
	def __init__(self):
		self.channel = []

	def reset(self) -> None:
		# Reset the channel
		self.channel = []
		
	def show_info(self) -> None:
		print("V2X: Packets: {}".format(self.channel.count))

