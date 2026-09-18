import unittest
import os
import database
import exporter

class TestExporterAndBackup(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_md_fuar_phase2.db")
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        database.init_db()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_payment_status_and_firm_summary(self):
        database.save_or_update_record("2026-09-15", "Sedef Firması", 10, 20000, 8000, "PAID", "Sedef 1")
        database.save_or_update_record("2026-09-16", "Sedef Firması", 5, 10000, 4000, "PARTIAL", "Sedef 2")
        database.save_or_update_record("2026-09-17", "Aşo Fuarcılık", 8, 16000, 6000, "PENDING", "Aşo 1")

        summary = database.get_firm_summary()
        self.assertEqual(len(summary), 2)
        
        sedef = next(s for s in summary if s["firm_name"] == "Sedef Firması")
        self.assertEqual(sedef["total_yovmiye"], 15.0)
        self.assertEqual(sedef["total_received"], 30000.0)
        self.assertEqual(sedef["partial_count"], 1)

    def test_excel_export(self):
        database.save_or_update_record("2026-09-15", "Sedef Firması", 10, 20000, 8000, "PAID", "Sedef Fuar 1")
        database.save_or_update_record("2026-09-16", "Sedef Firması", 5, 10000, 4000, "PARTIAL", "Sedef Fuar 2")

        test_excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_report.xlsx")
        if os.path.exists(test_excel_path):
            os.remove(test_excel_path)

        count = exporter.generate_weekly_excel_report("2026-09-15", "2026-09-21", "Sedef", test_excel_path)
        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(test_excel_path))

        if os.path.exists(test_excel_path):
            os.remove(test_excel_path)

    def test_auto_backup(self):
        backup_path = database.auto_backup_db()
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        if os.path.exists(backup_path):
            os.remove(backup_path)

if __name__ == "__main__":
    unittest.main()
