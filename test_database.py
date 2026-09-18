import unittest
import os
import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_md_fuar.db")
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        database.init_db()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_save_and_get_record(self):
        database.save_or_update_record(
            record_date="2026-09-18",
            firm_name="A Firması - Fuar Stant",
            yovmiye=18.0,
            amount_received=25000.0,
            worker_expense=10000.0,
            notes="Malzemeler teslim alındı"
        )

        rec = database.get_record("2026-09-18")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["firm_name"], "A Firması - Fuar Stant")
        self.assertEqual(rec["yovmiye"], 18.0)
        self.assertEqual(rec["amount_received"], 25000.0)
        self.assertEqual(rec["worker_expense"], 10000.0)
        self.assertEqual(rec["net_profit"], 15000.0)
        self.assertEqual(rec["notes"], "Malzemeler teslim alındı")

    def test_monthly_summary(self):
        database.save_or_update_record("2026-09-10", "Firma 1", 10, 10000, 4000, "Not 1")
        database.save_or_update_record("2026-09-18", "Firma 2", 8, 15000, 6000, "Not 2")

        summary = database.get_monthly_summary(2026, 9)
        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["total_yovmiye"], 18.0)
        self.assertEqual(summary["total_received"], 25000.0)
        self.assertEqual(summary["total_expense"], 10000.0)
        self.assertEqual(summary["total_net"], 15000.0)

    def test_update_and_delete(self):
        database.save_or_update_record("2026-09-18", "Eski Firma", 5, 5000, 2000, "Not")
        database.save_or_update_record("2026-09-18", "Yeni Firma", 6, 6000, 2500, "Not Güncellendi")

        rec = database.get_record("2026-09-18")
        self.assertEqual(rec["firm_name"], "Yeni Firma")
        self.assertEqual(rec["net_profit"], 3500.0)

        database.delete_record("2026-09-18")
        self.assertIsNone(database.get_record("2026-09-18"))

if __name__ == "__main__":
    unittest.main()
