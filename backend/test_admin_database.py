"""Run from the project root: python3 -m unittest -v test_admin_database.
Only touches a disposable temporary database, never freelancerApp.db.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from backend import admin_database as db


class AdminCRUDTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        previous = db.DB_NAME
        self.addCleanup(setattr, db, 'DB_NAME', previous)
        db.DB_NAME = Path(self.temp.name) / 'test.db'
        # Synthetic schema: tests CRUD behavior, not the user's live schema.
        with sqlite3.connect(db.DB_NAME) as conn:
            for table in db.TABLES:
                extra = ', FreelancerID INTEGER REFERENCES freelancers(ID)' if table == 'projects' else ''
                conn.execute(f'CREATE TABLE "{table}" (ID INTEGER PRIMARY KEY, Name TEXT NOT NULL, Notes TEXT DEFAULT "new"{extra})')

    def test_all_eight_tables(self):
        for table in db.TABLES:
            with self.subTest(table=table):
                key = db.create_record(table, {'Name': 'Example'})
                self.assertEqual(db.get_records(table)[0]['Notes'], 'new')
                self.assertEqual(db.update_record(table, key, {'Name': 'Updated'}), 1)
                self.assertEqual(db.get_records(table)[0]['Name'], 'Updated')
                self.assertEqual(db.delete_record(table, key), 1)
                self.assertEqual(db.get_records(table), [])

    def test_restricted_delete_and_recovery(self):
        freelancer = db.create_record('freelancers', {'Name': 'John Doe'})
        project = db.create_record('projects', {'Name': 'Project', 'FreelancerID': freelancer})
        with self.assertRaises(sqlite3.IntegrityError):
            db.delete_record('freelancers', freelancer)
        self.assertEqual(len(db.get_records('freelancers')), 1)
        # This must still work after an exception: no leaked write lock.
        db.update_record('projects', project, {'FreelancerID': None})
        self.assertEqual(db.delete_record('freelancers', freelancer), 1)

    def test_reject_bad_identifiers(self):
        with self.assertRaises(ValueError):
            db.get_records('not_a_table')
        with self.assertRaises(ValueError):
            db.create_record('clients', {'ID': 9})
        with self.assertRaises(ValueError):
            db.create_record('clients', {'unknown': 'x'})

    def test_missing_database_not_created(self):
        db.DB_NAME = Path(self.temp.name) / 'missing.db'
        with self.assertRaises(sqlite3.OperationalError):
            db.get_records('clients')
        self.assertFalse(db.DB_NAME.exists())


if __name__ == '__main__':
    unittest.main()
