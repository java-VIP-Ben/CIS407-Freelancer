"""Run from the project root; never writes to the real database."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from backend import database as db, listings_database as listings


class BookingPricesTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'test.db'
        for module in (db, listings):
            self.addCleanup(setattr, module, 'DB_NAME', module.DB_NAME)
            module.DB_NAME = path
        with sqlite3.connect(path) as conn:
            conn.executescript('''
                CREATE TABLE clients(ClientID INTEGER PRIMARY KEY, Name TEXT);
                CREATE TABLE freelancers(FreelancerID INTEGER PRIMARY KEY, Name TEXT);
                CREATE TABLE projects(ProjectID INTEGER PRIMARY KEY, ClientID INTEGER REFERENCES clients, FreelancerID INTEGER REFERENCES freelancers, ProposalID INTEGER REFERENCES proposals);
                CREATE TABLE proposals(ProposalID INTEGER PRIMARY KEY, ProposalName TEXT NOT NULL, ProjectID INTEGER REFERENCES projects, DateUpdated TEXT);
                CREATE TABLE listings(ListingID INTEGER PRIMARY KEY AUTOINCREMENT, FreelancerID INTEGER NOT NULL REFERENCES freelancers, JobTitle TEXT, Description TEXT, Skills TEXT, Category TEXT, CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP);
                INSERT INTO clients VALUES(1,'Client A'),(2,'Client B');
                INSERT INTO freelancers VALUES(1,'Freelancer A'),(2,'Freelancer B');
                INSERT INTO listings(FreelancerID,JobTitle,Description,Skills,Category) VALUES(1,'Old listing','Description','Skill','');
                INSERT INTO projects(ProjectID,ClientID,FreelancerID) VALUES(99,1,1);
                INSERT INTO proposals(ProposalID,ProposalName,ProjectID) VALUES(99,'Legacy proposal',99);
            ''')
        db.initialize_project_workflow()
        listings.initialize_listings()
        self.project = db.create_client_project(1, 'Example project')
        self.listing = listings.create_listing(1,'New listing','Description','Skill','Category',12550)

    def quote(self, expected=12550, client=1, freelancer=1, listing=None):
        return db.create_project_proposal(self.project, freelancer, client,
                listing_id=self.listing if listing is None else listing, expected_price_cents=expected)

    def test_decimal_validation(self):
        for text, cents in [('125.50',12550),('0',0),('1.2',120),('9999999.99',999999999)]:
            self.assertEqual(listings.parse_price(text), cents)
        for text in ('', '-1', '1.001', 'NaN', 'Infinity', '1e3', '10000000'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                listings.parse_price(text)
        self.assertEqual(listings.format_price(12550),'$125.50')
        self.assertEqual(listings.format_price(0),'$0.00')

    def test_migration_preserves_old_rows(self):
        db.initialize_project_workflow()
        listings.initialize_listings()
        rows = {r['ListingID']:r for r in listings.get_listings()}
        self.assertIsNone(rows[1]['PriceCents'])
        self.assertEqual(rows[1]['JobTitle'],'Old listing')
        self.assertEqual(rows[self.listing]['PriceCents'],12550)
        with db.workflow_connection() as conn:
            self.assertIsNone(conn.execute('SELECT PriceCents FROM proposals WHERE ProposalID=99').fetchone()[0])

    def test_snapshot_accept_and_listing_delete(self):
        proposal = self.quote()
        listings.update_listing(self.listing,1,'New listing','Description','Skill','Category',20000)
        self.assertEqual(db.get_freelancer_proposals(1,include_price=True)[0][-1],12550)
        self.assertIsNone(db.get_projects_for_client(1,include_price=True)[0][-1])
        self.assertEqual(db.respond_to_project_proposal(proposal,1,True),1)
        self.assertEqual(db.get_projects_for_client(1,include_price=True)[0][-1],12550)
        self.assertEqual(db.get_projects_for_freelancer(1,include_price=True)[0][-1],12550)
        listings.delete_listing(self.listing)
        self.assertEqual(db.get_projects_for_client(1,include_price=True)[0][-1],12550)

    def test_reject_stale_unpriced_wrong_owner_and_wrong_freelancer(self):
        for kwargs in ({'expected':100}, {'listing':1}, {'client':2}, {'freelancer':2}, {'listing':999}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.quote(**kwargs)
        self.assertEqual(db.get_freelancer_proposals(1),[])

    def test_declined_replacement_keeps_accepted_price(self):
        first = self.quote()
        db.respond_to_project_proposal(first,1,True)
        second_listing = listings.create_listing(2,'Other','Description','Skill','',9900)
        second = self.quote(9900,freelancer=2,listing=second_listing)
        db.respond_to_project_proposal(second,2,False)
        self.assertEqual(db.get_projects_for_client(1,include_price=True)[0][-1],12550)
        third = self.quote(9900,freelancer=2,listing=second_listing)
        db.respond_to_project_proposal(third,2,True)
        self.assertEqual(db.get_projects_for_client(1,include_price=True)[0][-1],9900)

    def test_zero_price_and_old_update_compatibility(self):
        listings.update_listing(self.listing,1,'Free','Description','Skill','',0)
        listings.update_listing(self.listing,1,'Renamed','Description','Skill','')
        proposal = self.quote(0)
        self.assertEqual(db.get_freelancer_proposals(1,include_price=True)[0][-1],0)
        db.respond_to_project_proposal(proposal,1,True)
        self.assertEqual(db.get_projects_for_client(1,include_price=True)[0][-1],0)


if __name__ == '__main__':
    unittest.main()
