import unittest
import os
import json
import database
import web_app

class TestWebApp(unittest.TestCase):
    def setUp(self):
        database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_md_fuar_web.db")
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)
        database.init_db()

        web_app.app.testing = True
        self.client = web_app.app.test_client()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html_content = response.data.decode("utf-8")
        self.assertIn("MD FUAR TAKİP", html_content)

    def test_record_post_and_get_api(self):
        payload = {
            "record_date": "2026-09-18",
            "firm_name": "Sedef Firması - Mobil Test",
            "yovmiye": 15.0,
            "amount_received": 30000.0,
            "worker_expense": 12000.0,
            "payment_status": "PARTIAL",
            "notes": "Sedef fuar kurulumu mobil test"
        }

        res_post = self.client.post("/api/record", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res_post.status_code, 200)

        res_get = self.client.get("/api/record/2026-09-18")
        self.assertEqual(res_get.status_code, 200)
        data = json.loads(res_get.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["firm_name"], "Sedef Firması - Mobil Test")
        self.assertEqual(data["data"]["net_profit"], 18000.0)

    def test_firm_summary_api(self):
        database.save_or_update_record("2026-09-15", "Sedef Firması", 10, 20000, 8000, "PAID", "Sedef 1")
        database.save_or_update_record("2026-09-16", "Sedef Firması", 5, 10000, 4000, "PARTIAL", "Sedef 2")

        res = self.client.get("/api/firm-summary")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 1)
        self.assertEqual(data["data"][0]["total_yovmiye"], 15.0)

if __name__ == "__main__":
    unittest.main()
