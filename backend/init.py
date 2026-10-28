import pandas as pd
import numpy as np
import sqlite3
import time

# ---------------------------------------
data = pd.DataFrame({
    "CustomerID": np.arange(1, 100001),
    "Region": np.random.choice(["North", "South", "East", "West"], 100000),
    "Sales": np.random.randint(10, 5000, 100000),
    "Category": np.random.choice(["Electronics", "Clothing", "Home", "Food"], 100000)
})

# ---------------------------------------
# 2. Create SQLite database and table
# ---------------------------------------
conn = sqlite3.connect("freelancerApp.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS projects")
cur.execute("DROP TABLE IF EXISTS freelancers")
cur.execute("DROP TABLE IF EXISTS clients")
cur.execute("DROP TABLE IF EXISTS payments")
cur.execute("DROP TABLE IF EXISTS proposals")
cur.execute("DROP TABLE IF EXISTS reviews")
cur.execute("DROP TABLE IF EXISTS skillsList")
cur.execute("DROP TABLE IF EXISTS milestones")

cur.execute("""
CREATE TABLE projects (
    ProjectID INTEGER PRIMARY KEY NOT NULL,
    FreelancerID INTEGER,
    ClientID INTEGER,
    PaymentID INTEGER,
    SkillsID INTEGER,
    MilestonesID INTEGER,
    ProposalID INTEGER,

    -- Foreign Key Constraints
    FOREIGN KEY (FreelancerID) REFERENCES freelancers(FreelancerID),
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID),
    FOREIGN KEY (PaymentID) REFERENCES Payments(PaymentID),
    FOREIGN KEY (SkillsID) REFERENCES Skills(SkillsID),
    FOREIGN KEY (MilestonesID) REFERENCES Milestones(MilestonesID),
    FOREIGN KEY (ProposalID) REFERENCES Proposals(ProposalID),
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

        -- Foreign Key Constraints
        FOREIGN KEY (SkillsListID) REFERENCES skillsList(skillsListID),
        FOREIGN KEY (ReviewsID) REFERENCES reviews(ReviewsID),
    )    
""")

cur.execute("""
    CREATE TABLE clients ( 
        ClientID INTEGER PRIMARY KEY NOT NULL,
        Name VARCHAR(50),
        Address TEXT,
        Phone TEXT,
        Email TEXT,
    )
""")

cur.execute("""
    CREATE TABLE payments (
        PaymentID INTEGER PRIMARY KEY NOT NULL,
        PriceTotal FLOAT,
        CurrentBalance FLOAT,
        DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP, 
        DateUpdated DATE,
    )    
""")

cur.execute("""
    CREATE TABLE proposals (
        ProposalsID INTEGER PRIMARY KEY NOT NULL,
        ProposalName TEXT NOT NULL,
        ProjectID INTGER,
        DateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
        DateUpdated DATE,

        -- Foreign Key Constraints
        FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID), 
    )
""")

cur.execute("""
    CREATE TABLE reviews (
        ReviewsID INTEGER PRIMARY KEY NOT NULL,
        Reviewer VARCHAR(50),
        Stars INTEGER,
        Comments TEXT,
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
        HumanResources BOOLEAN CHECK (HumanResources IN (0, 1)),
    )
""")

cur.execute("""
    CREATE TABLE milestones (
        MilestonesID INTEGER PRIMARY KEY NOT NULL,
        MilestoneName VARCHAR(50) NOT NULL,
        PercentageCompleted FLOAT, 
        DateStarted DATE,
        DateUpdated DATE,
    )
""")

# Insert data
data.to_sql("sales", conn, if_exists="append", index=False)

# ---------------------------------------
# 3. Row-oriented update simulation (OLTP)
# ---------------------------------------
start = time.time()
cur.execute("UPDATE sales SET Sales = Sales + 10 WHERE Region = 'North'")
conn.commit()
print("Row-oriented update (SQL):", round(time.time() - start, 3), "seconds")

# ---------------------------------------
# 4. Column-oriented query simulation (OLAP)
# ---------------------------------------
start = time.time()
df_result = pd.read_sql_query("SELECT Category, SUM(Sales) as TotalSales FROM sales GROUP BY Category", conn)
print("Column-oriented aggregation (SQL):", round(time.time() - start, 3), "seconds")
print(df_result)

# ---------------------------------------
# 5. Hash-index style lookup (using index)
# ---------------------------------------
start = time.time()
df_lookup = pd.read_sql_query("SELECT * FROM sales WHERE CustomerID = 25000", conn)
print("Hash-style lookup (SQL):", round(time.time() - start, 6), "seconds")
print(df_lookup)

# Close connection
conn.close()

