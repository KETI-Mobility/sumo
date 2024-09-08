import io
import sys		
import unittest
import GlobalSim
from Vehicle import Vehicle, N_VEH, _C_VEH, C_VEH, CE_VEH, T_CDA, E_CDA


class TestVehicle(unittest.TestCase):
	def test_vehicle_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "Generic"

		vehicle = Vehicle(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(vehicle.time_birth, time_birth)
		self.assertEqual(vehicle.vehicle_id, vehicle_id)
		self.assertEqual(vehicle.vehicle_type, vehicle_type)
		

class TestN_VEH(unittest.TestCase):
	def test_n_veh_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "N-VEH"

		nveh = N_VEH(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(nveh.time_birth, time_birth)
		self.assertEqual(nveh.vehicle_id, vehicle_id)
		self.assertEqual(nveh.vehicle_type, vehicle_type)
		self.assertEqual(nveh.state, N_VEH.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "N-VEH"

		nveh = N_VEH(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		captured_output = io.StringIO()
		sys.stdout = captured_output
		nveh.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[N-VEH] Vehicle ID: 1, Type: N-VEH", captured_output.getvalue())


class Test_C_VEH(unittest.TestCase):
	def test_c_veh_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "C-VEH"

		cveh = _C_VEH(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(cveh.time_birth, time_birth)
		self.assertEqual(cveh.vehicle_id, vehicle_id)
		self.assertEqual(cveh.vehicle_type, vehicle_type)
		self.assertEqual(cveh.state, _C_VEH.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "C-VEH"

		cveh = _C_VEH(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		import io
		import sys
		captured_output = io.StringIO()
		sys.stdout = captured_output
		cveh.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[C-VEH] Vehicle ID: 1, Type: C-VEH", captured_output.getvalue())


class TestC_VEH(unittest.TestCase):
	def test_c_veh_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "C-VEH"

		cveh = C_VEH(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(cveh.time_birth, time_birth)
		self.assertEqual(cveh.vehicle_id, vehicle_id)
		self.assertEqual(cveh.vehicle_type, vehicle_type)
		self.assertEqual(cveh.state, C_VEH.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "C-VEH"

		cveh = C_VEH(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		import io
		import sys
		captured_output = io.StringIO()
		sys.stdout = captured_output
		cveh.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[C-VEH] Vehicle ID: 1, Type: C-VEH", captured_output.getvalue())


class TestCE_VEH(unittest.TestCase):
	def test_ce_veh_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "CE-VEH"

		ceveh = CE_VEH(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(ceveh.time_birth, time_birth)
		self.assertEqual(ceveh.vehicle_id, vehicle_id)
		self.assertEqual(ceveh.vehicle_type, vehicle_type)
		self.assertEqual(ceveh.state, CE_VEH.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "CE-VEH"

		ceveh = CE_VEH(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		import io
		import sys
		captured_output = io.StringIO()
		sys.stdout = captured_output
		ceveh.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[CE-VEH] Vehicle ID: 1, Type: CE-VEH", captured_output.getvalue())

class TestT_CDA(unittest.TestCase):
	def test_t_cda_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "T-CDA"

		tcda = T_CDA(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(tcda.time_birth, time_birth)
		self.assertEqual(tcda.vehicle_id, vehicle_id)
		self.assertEqual(tcda.vehicle_type, vehicle_type)
		self.assertEqual(tcda.state, T_CDA.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "T-CDA"

		tcda = T_CDA(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		import io
		import sys
		captured_output = io.StringIO()
		sys.stdout = captured_output
		tcda.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[T-CDA] Vehicle ID: 1, Type: T-CDA", captured_output.getvalue())

class TestE_CDA(unittest.TestCase):
	def test_e_cda_initialization(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "E-CDA"

		ecda = E_CDA(time_birth, vehicle_id, vehicle_type)

		self.assertEqual(ecda.time_birth, time_birth)
		self.assertEqual(ecda.vehicle_id, vehicle_id)
		self.assertEqual(ecda.vehicle_type, vehicle_type)
		self.assertEqual(ecda.state, E_CDA.State.INITIAL)

	def test_show_info(self):
		time_birth = 0
		vehicle_id = 1
		vehicle_type = "E-CDA"

		ecda = E_CDA(time_birth, vehicle_id, vehicle_type)
		
		# Capture the output of show_info
		import io
		import sys
		captured_output = io.StringIO()
		sys.stdout = captured_output
		ecda.show_info()
		sys.stdout = sys.__stdout__

		self.assertIn("[E-CDA] Vehicle ID: 1, Type: E-CDA", captured_output.getvalue())



if __name__ == '__main__':
	unittest.main()
