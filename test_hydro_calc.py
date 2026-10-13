import unittest

import hydro_calc as hc


class CylinderTests(unittest.TestCase):
    def test_push_force(self):
        # 100 бар на поршне 100 мм дают около 78,54 кН
        self.assertAlmostEqual(hc.cylinder_force_kn(100, 100), 78.54, places=2)

    def test_pull_force_is_smaller(self):
        push = hc.cylinder_force_kn(100, 100)
        pull = hc.cylinder_force_kn(100, 100, 50)
        self.assertAlmostEqual(pull, 58.90, places=2)
        self.assertLess(pull, push)

    def test_speed(self):
        # 10 л/мин на поршне 100 мм дают около 21,2 мм/с
        self.assertAlmostEqual(hc.cylinder_speed_mm_s(10, 100), 21.22, places=2)

    def test_rod_bigger_than_bore(self):
        with self.assertRaises(ValueError):
            hc.cylinder_force_kn(100, 50, 60)

    def test_negative_pressure(self):
        with self.assertRaises(ValueError):
            hc.cylinder_force_kn(-5, 100)


class PumpTests(unittest.TestCase):
    def test_flow(self):
        # 32 см³/об * 1500 об/мин * 0,95 = 45,6 л/мин
        self.assertAlmostEqual(hc.pump_flow_l_min(32, 1500, 0.95), 45.6, places=2)

    def test_power(self):
        # 60 л/мин при 100 бар и КПД 1 дают 10 кВт
        self.assertAlmostEqual(hc.pump_power_kw(60, 100), 10.0, places=2)

    def test_power_with_efficiency(self):
        self.assertAlmostEqual(hc.pump_power_kw(60, 100, 0.8), 12.5, places=2)

    def test_bad_efficiency(self):
        with self.assertRaises(ValueError):
            hc.pump_power_kw(60, 100, 1.5)


class PipeTests(unittest.TestCase):
    def test_velocity(self):
        # 60 л/мин в трубе 20 мм дают около 3,18 м/с
        self.assertAlmostEqual(hc.pipe_velocity_m_s(60, 20), 3.18, places=2)

    def test_note_in_range(self):
        self.assertIn("в пределах", hc.velocity_note(4.0, "pressure"))

    def test_note_too_high(self):
        self.assertIn("выше", hc.velocity_note(8.0, "pressure"))

    def test_note_too_low(self):
        self.assertIn("ниже", hc.velocity_note(0.2, "suction"))

    def test_unknown_line(self):
        with self.assertRaises(ValueError):
            hc.velocity_note(1.0, "other")


if __name__ == "__main__":
    unittest.main()
