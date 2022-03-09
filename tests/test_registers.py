import unittest

from cpu.registers import Registers


class TestRegisters(unittest.TestCase):
    def setUp(self) -> None:
        self.registers = Registers()

    def test_large_values_are_truncated(self):
        self.registers.a = 0xdeadbeef
        self.assertEqual(self.registers.a, 0xef, 'value larger than one byte is not truncated')

    def test_get_af_register(self):
        self.registers.a = 0x12
        self.assertEqual(self.registers.af, 0x1200)
        self.registers.f = 0x34
        self.assertEqual(self.registers.af, 0x1234)

    def test_set_af_register(self):
        self.registers.af = 0x1337
        self.assertEqual(self.registers.a, 0x13)
        self.assertEqual(self.registers.f, 0x37)

    def test_get_bc_register(self):
        self.registers.b = 0x12
        self.assertEqual(self.registers.bc, 0x1200)
        self.registers.c = 0x34
        self.assertEqual(self.registers.bc, 0x1234)

    def test_set_bc_register(self):
        self.registers.bc = 0x1337
        self.assertEqual(self.registers.b, 0x13)
        self.assertEqual(self.registers.c, 0x37)

    def test_get_de_register(self):
        self.registers.d = 0x12
        self.assertEqual(self.registers.de, 0x1200)
        self.registers.e = 0x34
        self.assertEqual(self.registers.de, 0x1234)

    def test_set_de_register(self):
        self.registers.de = 0x1337
        self.assertEqual(self.registers.d, 0x13)
        self.assertEqual(self.registers.e, 0x37)

    def test_get_hl_register(self):
        self.registers.h = 0x12
        self.assertEqual(self.registers.hl, 0x1200)
        self.registers.l = 0x34
        self.assertEqual(self.registers.hl, 0x1234)

    def test_set_hl_register(self):
        self.registers.hl = 0x1337
        self.assertEqual(self.registers.h, 0x13)
        self.assertEqual(self.registers.l, 0x37)

    def test_set_z_flag(self) -> None:
        self.registers.z_flag = True

        self.assertTrue(self.registers.z_flag)
        self.assertFalse(self.registers.n_flag)
        self.assertFalse(self.registers.h_flag)
        self.assertFalse(self.registers.c_flag)

    def test_set_n_flag(self) -> None:
        self.registers.n_flag = True

        self.assertFalse(self.registers.z_flag)
        self.assertTrue(self.registers.n_flag)
        self.assertFalse(self.registers.h_flag)
        self.assertFalse(self.registers.c_flag)

    def test_set_h_flag(self) -> None:
        self.registers.h_flag = True

        self.assertFalse(self.registers.z_flag)
        self.assertFalse(self.registers.n_flag)
        self.assertTrue(self.registers.h_flag)
        self.assertFalse(self.registers.c_flag)

    def test_set_c_flag(self) -> None:
        self.registers.c_flag = True

        self.assertFalse(self.registers.z_flag)
        self.assertFalse(self.registers.n_flag)
        self.assertFalse(self.registers.h_flag)
        self.assertTrue(self.registers.c_flag)

    def test_reset_z_flag(self) -> None:
        self.registers.z_flag = True
        self.registers.n_flag = True
        self.registers.h_flag = True
        self.registers.c_flag = True

        self.registers.z_flag = False

        self.assertFalse(self.registers.z_flag)
        self.assertTrue(self.registers.n_flag)
        self.assertTrue(self.registers.h_flag)
        self.assertTrue(self.registers.c_flag)


if __name__ == '__main__':
    unittest.main()
