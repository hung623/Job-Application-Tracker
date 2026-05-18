import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

import app


class AppDbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_db_path = app.DB_PATH
        app.DB_PATH = Path(self.tmp.name) / "test_applications.db"
        app.init_db()

    def tearDown(self):
        app.DB_PATH = self.original_db_path
        self.tmp.cleanup()

    def test_add_and_load_application(self):
        app.add_application(
            {
                "company_name": "Acme",
                "job_title": "Engineer",
                "status": "Applied",
                "notes": "Initial application",
                "deadline": date.today().isoformat(),
                "source": "LinkedIn",
                "priority": "High",
                "follow_up_date": date.today().isoformat(),
                "job_url": "https://example.com/job/1",
            }
        )

        df = app.load_applications()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["company_name"], "Acme")
        self.assertEqual(df.iloc[0]["status"], "Applied")

    def test_bulk_update_and_delete(self):
        app.add_application(
            {
                "company_name": "Beta",
                "job_title": "Analyst",
                "status": "Applied",
                "notes": "n",
                "deadline": None,
                "source": "Indeed",
                "priority": "Low",
                "follow_up_date": None,
                "job_url": "",
            }
        )
        df = app.load_applications()
        app_id = int(df.iloc[0]["id"])

        changed = app.bulk_update_applications(
            [
                {
                    "id": app_id,
                    "status": "Interview",
                    "priority": "Medium",
                    "source": "Referral",
                    "deadline": None,
                    "follow_up_date": None,
                    "notes": "updated",
                    "job_url": "https://example.com/job/2",
                }
            ]
        )
        self.assertEqual(changed, 1)

        updated = app.load_applications()
        self.assertEqual(updated.iloc[0]["status"], "Interview")

        app.delete_application(app_id)
        final_df = app.load_applications()
        self.assertEqual(len(final_df), 0)


if __name__ == "__main__":
    unittest.main()
