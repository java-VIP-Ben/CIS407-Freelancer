"""Tests run exclusively against a temporary SQLite database."""
import sqlite3
import tempfile
import unittest
import gc
from pathlib import Path
from backend import listings_database as db


class ListingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(gc.collect)
        original = db.DB_NAME
        self.addCleanup(setattr, db, "DB_NAME", original)
        db.DB_NAME = Path(self.temp.name) / "test.db"
        with sqlite3.connect(db.DB_NAME) as conn:
            conn.executescript("""
                CREATE TABLE freelancers (FreelancerID INTEGER PRIMARY KEY, Name TEXT,
                    SkillsListID INTEGER, Email TEXT, Phone TEXT, ReviewsID INTEGER);
                INSERT INTO freelancers (FreelancerID, Name) VALUES (5, 'John Doe'), (6, 'Jane Smith');
                CREATE TABLE projects (ProjectID INTEGER PRIMARY KEY, FreelancerID INTEGER);
                INSERT INTO projects VALUES (1, 5);
                CREATE TABLE reviews (
                    ReviewsID INTEGER PRIMARY KEY,
                    Reviewer TEXT,
                    Stars INTEGER,
                    Comments TEXT
                );
                CREATE TABLE freelancer_reviews (
                    ReviewsID INTEGER PRIMARY KEY,
                    ProjectID INTEGER,
                    ClientID INTEGER,
                    FreelancerID INTEGER
                );
                INSERT INTO reviews VALUES
                    (1, 'Client One', 4, 'Good'),
                    (2, 'Client Two', 5, 'Great');
                INSERT INTO freelancer_reviews VALUES
                    (1, 1, 1, 5), (2, 2, 2, 5);
            """)
        db.initialize_listings()

    def seed(self):
        a = db.create_listing(5, "Web Developer", "Build responsive websites", "Python, React", "Technology")
        b = db.create_listing(6, "Logo Designer", "Custom brand designs", "Illustration, Figma", "Design")
        return a, b

    def test_migration_preserves_records_and_is_repeatable(self):
        self.seed()
        db.initialize_listings()
        self.assertEqual(len(db.get_listings()), 2)
        self.assertEqual(len(db.get_freelancer_options()), 2)
        with db.connection() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0], 1)

    def test_crud(self):
        a, b = self.seed()
        self.assertEqual(db.get_listings()[0]["ListingID"], b)
        self.assertEqual(db.update_listing(a, 6, "New title", "New desc", "SQL", "Tech"), 1)
        self.assertEqual(db.search_listings("New title", "Job / title")[0]["Name"], "Jane Smith")
        self.assertEqual(db.delete_listing(a), 1)
        self.assertEqual(db.delete_listing(a), 0)
        self.assertEqual(len(db.get_listings()), 1)
        self.assertEqual(len(db.get_freelancer_options()), 2)

    def test_listing_rows_include_average_freelancer_reviews(self):
        _, _ = self.seed()
        rows = {row["FreelancerID"]: row for row in db.get_listings()}
        self.assertEqual(rows[5]["AverageRating"], 4.5)
        self.assertEqual(rows[5]["ReviewCount"], 2)
        self.assertIsNone(rows[6]["AverageRating"])
        self.assertEqual(rows[6]["ReviewCount"], 0)

    def test_listing_rows_work_without_review_tables(self):
        self.seed()
        with db.connection() as conn:
            conn.execute("DROP TABLE freelancer_reviews")
            conn.execute("DROP TABLE reviews")
        rows = db.get_listings()
        self.assertTrue(all(row["AverageRating"] is None for row in rows))
        self.assertTrue(all(row["ReviewCount"] == 0 for row in rows))

    def test_freelancer_scoped_listings(self):
        a, b = self.seed()
        self.assertEqual(
            [row["ListingID"] for row in db.get_listings_for_freelancer(5)],
            [a],
        )
        self.assertEqual(
            db.update_listing_for_freelancer(
                b, 5, "Wrong owner", "Wrong owner", "Wrong owner"
            ),
            0,
        )
        self.assertEqual(db.delete_listing_for_freelancer(b, 5), 0)
        self.assertEqual(
            db.update_listing_for_freelancer(
                a, 5, "Freelancer title", "Freelancer description",
                "Freelancer skill", "Freelancer category", 2500
            ),
            1,
        )
        row = db.get_listings_for_freelancer(5)[0]
        self.assertEqual(row["JobTitle"], "Freelancer title")
        self.assertEqual(row["PriceCents"], 2500)
        self.assertEqual(db.delete_listing_for_freelancer(a, 5), 1)
        self.assertEqual([row["ListingID"] for row in db.get_listings_for_freelancer(5)], [])

    def test_every_search_field_and_multiword_search(self):
        a, b = self.seed()
        for field, term, expected in [
            ("Freelancer name", "JOHN", a), ("Job / title", "designer", b),
            ("Description", "responsive", a), ("Skills", "figma", b),
            ("Category", "technology", a), ("All fields", "john react responsive", a),
        ]:
            with self.subTest(field=field):
                self.assertEqual([r["ListingID"] for r in db.search_listings(term, field)], [expected])
        self.assertEqual(len(db.search_listings("   ")), 2)
        self.assertEqual(db.search_listings("john figma"), [])
        self.assertEqual(db.search_listings("%"), [])
        with self.assertRaises(ValueError):
            db.search_listings("anything", "bad field")

    def test_rename_is_reflected(self):
        a, _ = self.seed()
        with db.connection() as conn:
            conn.execute("UPDATE freelancers SET Name = 'John Updated' WHERE FreelancerID = 5")
        self.assertEqual(db.search_listings("Updated", "Freelancer name")[0]["ListingID"], a)

    def test_foreign_keys_and_transaction_cleanup(self):
        a, _ = self.seed()
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_listing(999, "Job", "Description", "Skill")
        with self.assertRaises(sqlite3.IntegrityError):
            db.update_listing(a, 999, "Job", "Description", "Skill")
        with self.assertRaises(sqlite3.IntegrityError):
            with db.connection() as conn:
                conn.execute("DELETE FROM freelancers WHERE FreelancerID=5")
        self.assertEqual(db.delete_listing(a), 1)
        with db.connection() as conn:
            conn.execute("DELETE FROM freelancers WHERE FreelancerID=5")
        self.assertEqual(len(db.get_freelancer_options()), 1)

    def test_validation_and_missing_database(self):
        with self.assertRaises(ValueError):
            db.create_listing(5, "   ", "Description", "Skill")
        with self.assertRaises(ValueError):
            db.create_listing(None, "Job", "Description", "Skill")
        with self.assertRaises(ValueError):
            db.create_listing(5, "Job", "Description", "")
        db.DB_NAME = Path(self.temp.name) / "missing.db"
        with self.assertRaises(sqlite3.OperationalError):
            db.initialize_listings()
        self.assertFalse(db.DB_NAME.exists())

    def test_missing_parent_table_is_rejected(self):
        with db.connection() as conn:
            conn.execute("DROP TABLE listings")
            conn.execute("DROP TABLE freelancers")
        with self.assertRaises(sqlite3.OperationalError):
            db.initialize_listings()


if __name__ == "__main__":
    unittest.main()
