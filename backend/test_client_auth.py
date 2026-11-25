"""Run from project root: python3 -m unittest -v test_client_auth.
All tests use a disposable DB initialized from the project's schema.
"""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from backend import client_auth as auth, database as db, admin_database as admin


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / 'test.db'
        for module in (auth, db, admin):
            self.addCleanup(setattr, module, 'DB_NAME', module.DB_NAME)
            module.DB_NAME = path
        # Legacy schema matching the uploaded database's relevant tables.
        with sqlite3.connect(path) as conn:
            conn.executescript('''
                CREATE TABLE clients (ClientID INTEGER PRIMARY KEY, Name TEXT, Address TEXT, Phone TEXT, Email TEXT);
                CREATE TABLE freelancers (FreelancerID INTEGER PRIMARY KEY, Name TEXT, SkillsListID INTEGER, Email TEXT, Phone TEXT, ReviewsID INTEGER);
                CREATE TABLE projects (ProjectID INTEGER PRIMARY KEY, FreelancerID INTEGER REFERENCES freelancers(FreelancerID), ClientID INTEGER REFERENCES clients(ClientID), PaymentID INTEGER, SkillsID INTEGER, MilestonesID INTEGER, ProposalID INTEGER REFERENCES proposals(ProposalID));
                CREATE TABLE proposals (ProposalID INTEGER PRIMARY KEY, ProposalName TEXT NOT NULL, ProjectID INTEGER REFERENCES projects(ProjectID), DateCreated TEXT DEFAULT CURRENT_TIMESTAMP, DateUpdated TEXT);
                INSERT INTO clients VALUES (1,'Legacy','Address','Phone','duplicate@example.test'), (2,'Legacy 2','Address','Phone','duplicate@example.test');
                INSERT INTO freelancers (FreelancerID, Name, Email) VALUES (1,'First freelancer','first@example.test'), (2,'Second freelancer','second@example.test');
                INSERT INTO projects (ProjectID,ClientID,FreelancerID) VALUES (10,1,1);
            ''')
        auth.initialize_auth()
        db.initialize_project_workflow()
        self.password = 'Example-long-password!'

    def register(self, email='new@example.test'):
        return auth.register_client('New client', email, 'Address', 'Phone', self.password)

    def test_migration_preserves_legacy_data_and_is_repeatable(self):
        auth.initialize_auth()
        db.initialize_project_workflow()
        self.assertEqual(len(db.get_client()), 2)
        self.assertEqual(db.get_projects()[0][0], 10)
        self.assertEqual(len(db.get_projects()[0]), 7)
        self.assertEqual(len(db.get_freelancers()[0]), 6)
        self.assertEqual(len(db.get_client()[0]), 5)
        self.assertIsNone(auth.authenticate_client('duplicate@example.test', self.password))

    def test_client_registration_and_password_login(self):
        cid = self.register()
        result = auth.authenticate_client(' NEW@example.test ', self.password)
        self.assertEqual(result['ClientID'], cid)
        self.assertNotIn('PasswordHash', result)
        self.assertIsNone(auth.authenticate_client('new@example.test', 'wrong'))
        self.assertIsNone(auth.authenticate_client('new@example.test', ''))
        with auth.connection() as conn:
            stored = conn.execute('SELECT PasswordHash FROM clients WHERE ClientID=?', (cid,)).fetchone()[0]
        self.assertNotEqual(stored, self.password)
        self.assertTrue(auth.verify_password(self.password, stored))
        self.assertNotEqual(stored, auth.hash_password(self.password))

    def test_duplicate_emails_and_activation(self):
        with self.assertRaises(ValueError):
            self.register('duplicate@example.test')
        with self.assertRaises(ValueError):
            auth.set_client_password(1, self.password)
        admin.update_record('clients', 1, {'Email': 'unique@example.test'})
        auth.set_client_password(1, self.password)
        self.assertEqual(auth.authenticate_client('unique@example.test', self.password)['ClientID'], 1)
        with self.assertRaises(sqlite3.IntegrityError):
            admin.update_record('clients', 2, {'Email': ' UNIQUE@example.test '})
        with self.assertRaises(sqlite3.IntegrityError):
            admin.update_record('clients', 1, {'Email': None})
        with self.assertRaises(ValueError):
            self.register('UNIQUE@example.test')

    def test_freelancer_requires_password(self):
        self.assertIsNone(auth.authenticate_freelancer('first@example.test', ''))
        auth.set_account_password('freelancer', 1, self.password)
        self.assertEqual(auth.authenticate_freelancer('FIRST@example.test', self.password)['FreelancerID'], 1)
        self.assertIsNone(auth.authenticate_freelancer('first@example.test', 'bad'))
        self.assertIsNone(auth.authenticate_client('first@example.test', self.password))

    def test_admin_protects_hashes(self):
        cid = self.register()
        for table, key in [('clients', cid), ('freelancers', 1)]:
            self.assertNotIn('PasswordHash', [c['name'] for c in admin.get_schema(table)['columns']])
            self.assertTrue(all('PasswordHash' not in row for row in admin.get_records(table)))
            with self.assertRaises(ValueError):
                admin.update_record(table, key, {'PasswordHash': 'not a hash'})
            with self.assertRaises(ValueError):
                admin.create_record(table, {'PasswordHash': 'not a hash'})

    def test_admin_login_config(self):
        with patch.dict(os.environ, {'FREELANCER_ADMIN_PASSWORD': ''}):
            self.assertFalse(auth.authenticate_admin('admin', 'admin'))
        with patch.dict(os.environ, {'FREELANCER_ADMIN_PASSWORD': self.password}):
            self.assertTrue(auth.authenticate_admin('admin', self.password))
            self.assertFalse(auth.authenticate_admin('admin', 'wrong'))

    def test_project_invitation_accept_decline_and_ownership(self):
        cid = self.register()
        pid = db.create_client_project(cid, 'New project')
        self.assertEqual(db.get_projects_for_client(cid), [(pid, 'New project', None, None)])
        self.assertNotIn(pid, [row[0] for row in db.get_projects_for_client(1)])
        with self.assertRaises(ValueError):
            db.create_project_proposal(pid, 1, 1)
        proposal = db.create_project_proposal(pid, 1, cid)
        with self.assertRaises(ValueError):
            db.create_project_proposal(pid, 1, cid)
        self.assertEqual(db.get_freelancer_proposals(2), [])
        self.assertEqual(db.respond_to_project_proposal(proposal, 2, True), 0)
        self.assertEqual(db.respond_to_project_proposal(proposal, 1, True), 1)
        self.assertEqual(db.get_projects_for_client(cid)[0][3], 1)
        self.assertEqual(db.get_projects_for_freelancer(1)[0][:3], (pid, 'New project', cid))
        self.assertEqual(db.get_freelancer_proposals(1)[0][6], 'accepted')
        proposal2 = db.create_project_proposal(pid, 2, cid)
        self.assertEqual(db.respond_to_project_proposal(proposal2, 2, False), 1)
        self.assertEqual(db.get_projects_for_client(cid)[0][3], 1)
        self.assertEqual(db.get_freelancer_proposals(2)[0][6], 'declined')
        self.assertEqual(db.respond_to_project_proposal(proposal2, 2, True), 0)
        proposal3 = db.create_project_proposal(pid, 2, cid)
        self.assertEqual(db.respond_to_project_proposal(proposal3, 2, True), 1)
        self.assertEqual(db.get_projects_for_client(cid)[0][3], 2)
        with db.workflow_connection() as conn:
            self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_validation(self):
        with self.assertRaises(ValueError):
            auth.register_client('X','bad-email','Address','Phone',self.password)
        with self.assertRaises(ValueError):
            auth.register_client('X','x@example.test','Address','Phone','short')
        self.assertFalse(auth.verify_password(self.password,'malformed'))


if __name__ == '__main__':
    unittest.main()
