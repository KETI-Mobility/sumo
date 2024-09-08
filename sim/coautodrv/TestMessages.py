import unittest
import GlobalSim
from Message import Message, BSM, BSMplus, EDM, DMM, DNMReq, DNMResp
from Vehicle import Vehicle


class TestMessage(unittest.TestCase):
	def setUp(self):
		# Reset GlobalSim.msg_id before each test
		GlobalSim.msg_id = 0

	def test_message_initialization(self):
		msg_type = Message.Type.MSG_BSM
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		message = Message(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(message.msg_id, 1)
		self.assertEqual(message.msg_type, msg_type)
		self.assertEqual(message.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(message.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(message.rsu_location, rsu_location)

	def test_show_msg(self):
		msg_type = Message.Type.MSG_BSM
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		message = Message(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)
		
		# Since show_msg does nothing, we just call it to ensure no exceptions are raised
		message.show_msg()


class TestBSM(unittest.TestCase):
	def test_bsm_initialization(self):
		msg_type = Message.Type.MSG_BSM
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		bsm = BSM(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(bsm.msg_id, 1)
		self.assertEqual(bsm.msg_type, msg_type)
		self.assertEqual(bsm.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(bsm.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(bsm.rsu_location, rsu_location)


class TestBSMplus(unittest.TestCase):
	def test_bsmplus_initialization(self):
		msg_type = Message.Type.MSG_BSMplus
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		bsmplus = BSMplus(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(bsmplus.msg_id, 1)
		self.assertEqual(bsmplus.msg_type, msg_type)
		self.assertEqual(bsmplus.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(bsmplus.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(bsmplus.rsu_location, rsu_location)


class TestEDM(unittest.TestCase):
	def test_edm_initialization(self):
		msg_type = Message.Type.MSG_EDM
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		edm = EDM(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(edm.msg_id, 1)
		self.assertEqual(edm.msg_type, msg_type)
		self.assertEqual(edm.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(edm.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(edm.rsu_location, rsu_location)


class TestDMM(unittest.TestCase):
	def test_dmm_initialization(self):
		msg_type = Message.Type.MSG_DMM
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		dmm = DMM(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(dmm.msg_id, 1)
		self.assertEqual(dmm.msg_type, msg_type)
		self.assertEqual(dmm.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(dmm.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(dmm.rsu_location, rsu_location)


class TestDNMReq(unittest.TestCase):
	def test_dnmreq_initialization(self):
		msg_type = Message.Type.MSG_DNMREQ
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		dnmreq = DNMReq(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(dnmreq.msg_id, 1)
		self.assertEqual(dnmreq.msg_type, msg_type)
		self.assertEqual(dnmreq.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(dnmreq.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(dnmreq.rsu_location, rsu_location)


class TestDNMResp(unittest.TestCase):
	def test_dnmresp_initialization(self):
		msg_type = Message.Type.MSG_DNMRESP
		sender_vehicle_id = 1
		sender_vehicle_type = "Car"
		rsu_location = (100, 200)

		dnmresp = DNMResp(msg_type, sender_vehicle_id, sender_vehicle_type, rsu_location)

		self.assertEqual(dnmresp.msg_id, 1)
		self.assertEqual(dnmresp.msg_type, msg_type)
		self.assertEqual(dnmresp.sender_vehicle_id, sender_vehicle_id)
		self.assertEqual(dnmresp.sender_vehicle_type, sender_vehicle_type)
		self.assertEqual(dnmresp.rsu_location, rsu_location)


if __name__ == '__main__':
	unittest.main()
