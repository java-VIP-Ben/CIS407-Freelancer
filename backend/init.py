import sqlite3
from pathlib import Path

# ---------------------------------------
# 1. Create SQLite database and table
# ---------------------------------------
DB_NAME = Path(__file__).resolve().parent / "freelancerApp.db"
conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

cur.execute("""
CREATE TABLE projects (
    ProjectID INTEGER PRIMARY KEY NOT NULL,
    FreelancerID INTEGER,
    ClientID INTEGER,
    PaymentID INTEGER,
    SkillsID INTEGER,
    MilestonesID INTEGER,
    ProposalID INTEGER,
    ProjectName TEXT,

    -- Foreign Key Constraints
    FOREIGN KEY (FreelancerID) REFERENCES freelancers(FreelancerID),
    FOREIGN KEY (ClientID) REFERENCES clients(ClientID),
    FOREIGN KEY (PaymentID) REFERENCES payments(PaymentID),
    FOREIGN KEY (SkillsID) REFERENCES skillsList(SkillsListID),
    FOREIGN KEY (MilestonesID) REFERENCES milestones(MilestonesID),
    FOREIGN KEY (ProposalID) REFERENCES proposals(ProposalID)
)
""")

cur.execute("""
    CREATE TABLE freelancers (
        FreelancerID INTEGER PRIMARY KEY NOT NULL,
        Name VARCHAR(50), 
        SkillsListID INTEGER,
        Email TEXT,
        Phone TEXT,
        ReviewsID INTEGER,
        PasswordHash TEXT,

        -- Foreign Key Constraints
        FOREIGN KEY (SkillsListID) REFERENCES skillsList(skillsListID),
        FOREIGN KEY (ReviewsID) REFERENCES reviews(ReviewsID)
    )    
""")

cur.execute("""
    CREATE TABLE clients ( 
        ClientID INTEGER PRIMARY KEY NOT NULL,
        Name VARCHAR(50),
        Address TEXT,
        Phone TEXT,
        Email TEXT,
        PasswordHash TEXT
    )
""")

cur.execute("""
    CREATE TABLE payments (
        PaymentID INTEGER PRIMARY KEY NOT NULL,
        PriceTotal FLOAT,
        CurrentBalance FLOAT,
        DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP, 
        DateUpdated DATE
    )    
""")

cur.execute("""
    CREATE TABLE proposals (
        ProposalID INTEGER PRIMARY KEY NOT NULL,
        ProposalName TEXT NOT NULL,
        ProjectID INTEGER,
        FreelancerID INTEGER REFERENCES freelancers(FreelancerID),
        Status TEXT NOT NULL DEFAULT 'pending' CHECK(Status IN ('pending','accepted','declined')),
        PriceCents INTEGER CHECK(PriceCents IS NULL OR (typeof(PriceCents) = 'integer' AND PriceCents BETWEEN 0 AND 999999999)),
        DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
        DateUpdated DATE,

        -- Foreign Key Constraints
        FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) 
    )
""")

cur.execute("""
    CREATE TABLE reviews (
        ReviewsID INTEGER PRIMARY KEY NOT NULL,
        Reviewer VARCHAR(50),
        Stars INTEGER,
        Comments TEXT
    )
""")

cur.execute("""
    CREATE TABLE skillsList (
        SkillsListID INTEGER PRIMARY KEY NOT NULL,
        Carpenter BOOLEAN CHECK (Carpenter IN (0, 1)),
        Mechanic BOOLEAN CHECK (Mechanic IN (0, 1)),
        Streamer BOOLEAN CHECK (Streamer IN (0, 1)),
        Plumber BOOLEAN CHECK (Plumber IN (0, 1)),
        Consultant BOOLEAN CHECK (Consultant IN (0, 1)),
        Therapist BOOLEAN CHECK (Therapist IN (0, 1)),
        Salesman BOOLEAN CHECK (Salesman IN (0, 1)),
        Engineer BOOLEAN CHECK (Engineer IN (0, 1)),
        Chef BOOLEAN CHECK (Chef IN (0, 1)),
        Manager BOOLEAN CHECK (Manager IN (0, 1)),
        HumanResources BOOLEAN CHECK (HumanResources IN (0, 1))
    )
""")

cur.execute("""
    CREATE TABLE milestones (
        MilestonesID INTEGER PRIMARY KEY NOT NULL,
        MilestoneName VARCHAR(50) NOT NULL,
        PercentageCompleted FLOAT, 
        DateStarted DATE,
        DateUpdated DATE
    )
""")

# Close connection
conn.commit()
conn.close()

