import sqlite3
import tempfile
import unittest
import gc
from pathlib import Path

from backend import database as db


class ProjectSummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(gc.collect)
        original = db.DB_NAME
        self.addCleanup(setattr, db, "DB_NAME", original)
        db.DB_NAME = Path(self.temp.name) / "test.db"
        with sqlite3.connect(db.DB_NAME) as conn:
            conn.executescript("""
                CREATE TABLE clients (ClientID INTEGER PRIMARY KEY, Name TEXT);
                CREATE TABLE freelancers (FreelancerID INTEGER PRIMARY KEY, Name TEXT);
                CREATE TABLE reviews (
                    ReviewsID INTEGER PRIMARY KEY,
                    Reviewer TEXT,
                    Stars INTEGER,
                    Comments TEXT
                );
                CREATE TABLE milestones (
                    MilestonesID INTEGER PRIMARY KEY,
                    MilestoneName TEXT NOT NULL,
                    PercentageCompleted FLOAT,
                    DateStarted DATE,
                    DateUpdated DATE
                );
                CREATE TABLE projects (
                    ProjectID INTEGER PRIMARY KEY,
                    ClientID INTEGER,
                    FreelancerID INTEGER,
                    MilestonesID INTEGER,
                    ProjectName TEXT,
                    ProposalID INTEGER
                );
                CREATE TABLE proposals (
                    ProposalID INTEGER PRIMARY KEY,
                    ProposalName TEXT NOT NULL,
                    ProjectID INTEGER
                );
                INSERT INTO clients VALUES (1, 'Client'), (2, 'Other client');
                INSERT INTO freelancers VALUES (5, 'Freelancer');
                INSERT INTO milestones VALUES (10, 'Legacy milestone', 50, NULL, NULL);
                INSERT INTO projects VALUES (20, 1, 5, 10, 'Website', NULL);
                INSERT INTO projects VALUES (21, 1, NULL, NULL, 'Unassigned', NULL);
            """)
        db.initialize_project_workflow()

    def test_summary_lists_multiple_milestones_and_tracks_progress(self):
        project = next(
            item for item in db.get_project_summaries("client", 1)
            if item["ProjectID"] == 20
        )
        self.assertEqual(project["Progress"], 50)
        self.assertEqual(
            [item["MilestoneName"] for item in project["Milestones"]],
            ["Legacy milestone"],
        )

        milestone_id = db.create_project_milestone(
            20, "client", 1, "Launch", date_started="2026-11-24"
        )
        self.assertEqual(db.update_project_milestone_progress(
            20, milestone_id, "client", 1, 100
        ), 1)
        project = db.get_project_summaries("freelancer", 5)[0]
        self.assertEqual(project["Progress"], 75)
        self.assertEqual(len(project["Milestones"]), 2)
        self.assertEqual(project["Milestones"][1]["PercentageCompleted"], 100)

    def test_milestone_operations_are_limited_to_project_participants(self):
        with self.assertRaises(ValueError):
            db.create_project_milestone(20, "client", 2, "Unauthorized")
        with self.assertRaises(ValueError):
            db.create_project_milestone(20, "freelancer", 5, "Freelancer edit")
        milestone_id = db.create_project_milestone(
            20, "client", 1, "Planning"
        )
        with self.assertRaises(ValueError):
            db.update_project_milestone_progress(
                20, milestone_id, "freelancer", 5, 80
            )
        self.assertEqual(db.update_project_milestone_progress(
            20, milestone_id, "client", 2, 80
        ), 0)
        with self.assertRaises(ValueError):
            db.create_project_milestone(20, "client", 1, "Bad progress", 101)
        with self.assertRaises(ValueError):
            db.create_project_milestone(20, "client", 1, "Bad date", date_started="tomorrow")

    def test_client_can_update_only_their_project_name(self):
        self.assertEqual(db.update_client_project(1, 20, "Updated website"), 1)
        project_name = next(
            row[1] for row in db.get_projects_for_client(1) if row[0] == 20
        )
        self.assertEqual(project_name, "Updated website")
        self.assertEqual(db.update_client_project(2, 20, "Unauthorized"), 0)
        project_name = next(
            row[1] for row in db.get_projects_for_client(1) if row[0] == 20
        )
        self.assertEqual(project_name, "Updated website")
        for invalid_name in (" ", "x" * 121):
            with self.subTest(name=invalid_name[:10]), self.assertRaises(ValueError):
                db.update_client_project(1, 20, invalid_name)

    def test_client_can_review_assigned_freelancer_once_per_project(self):
        review_id = db.create_freelancer_review(
            1, 20, 5, "Excellent work and communication."
        )
        review = db.get_project_review(20, "client", 1)
        self.assertEqual(review["ReviewsID"], review_id)
        self.assertEqual(review["Reviewer"], "Client")
        self.assertEqual(review["Stars"], 5)
        self.assertEqual(
            db.get_project_review(20, "freelancer", 5)["Comments"],
            "Excellent work and communication.",
        )
        with self.assertRaises(ValueError):
            db.create_freelancer_review(1, 20, 4, "Duplicate review")
        with self.assertRaises(ValueError):
            db.create_freelancer_review(2, 20, 5, "Not your project")
        with self.assertRaises(ValueError):
            db.create_freelancer_review(1, 21, 5, "No freelancer assigned")
        with self.assertRaises(ValueError):
            db.create_freelancer_review(1, 20, 6, "Invalid rating")


if __name__ == "__main__":
    unittest.main()
