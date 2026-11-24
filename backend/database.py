# Contains all of the CRUD / DB requests
# Order:
# 1 Freelancer
# 2 Projects  
#
#
#
#
#
#
#
#
#
#


import sqlite3
from pathlib import Path
DB_NAME = Path(__file__).resolve().parent / "freelancerApp.db"

def create_freelancer(name, email, phone):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO freelancers (Name, Email, Phone)
        VALUES (?, ?, ?)
    """, (name, email, phone))

    conn.commit()
    freelancer_id = cur.lastrowid
    conn.close()

    return freelancer_id

def get_freelancers():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM freelancers")
    freelancers = cur.fetchall()

    conn.close()
    return freelancers

def update_freelancer(freelancer_id, name, email, phone):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        UPDATE freelancers
        SET Name = ?, Email = ?, Phone = ?
        WHERE FreelancerID = ?
    """, (name, email, phone, freelancer_id))

    conn.commit()
    rows_updated = cur.rowcount
    conn.close()

    return rows_updated

def delete_freelancer(freelancer_id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM freelancers
            WHERE FreelancerID = ?
        """, (freelancer_id,))

        rows_deleted = cur.rowcount
        conn.commit()
        return rows_deleted
    
    except sqlite3.Error:
        conn.rollback()
        raise

    finally: 
        conn.close()

# Projects
def create_projects(freelancer_id, client_id, payment_id, skills_id, milestones_id, proposal_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO projects (FreelancerID, ClientID, PaymentID, SkillsID, MilestonesID, ProposalID)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (freelancer_id, client_id, payment_id, skills_id, milestones_id, proposal_id))

    conn.commit()
    project_id= cur.lastrowid
    conn.close()

    return project_id 

def get_projects():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    conn.close()
    return projects 

def update_projects(project_id, freelancer_id, client_id, payment_id, skills_id, milestones_id, proposal_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        UPDATE projects
        SET FreelancerID = ?,
        ClientID = ?,
        PaymentID = ?,
        SkillsID = ?,
        MilestonesID = ?, 
        ProposalID = ? 
        WHERE ProjectID = ?
    """, (freelancer_id, client_id, payment_id, skills_id, milestones_id, proposal_id, project_id))

    conn.commit()
    rows_updated = cur.rowcount
    conn.close()

    return rows_updated

def delete_projects(project_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM projects 
        WHERE ProjectID = ?
    """, (project_id,))

    conn.commit()
    rows_deleted = cur.rowcount
    conn.close()

    return rows_deleted

# Clients 
def create_client(name, address, email, phone):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clients (Name, Address, Email, Phone)
        VALUES (?, ?, ?, ?)
    """, (name, address, email, phone))

    conn.commit()
    client_id= cur.lastrowid
    conn.close()

    return client_id 

def get_client():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()

    conn.close()
    return clients 

def update_client(client_id, name, address, email, phone):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE clients 
        SET Name = ?,
        Address = ?, 
        Email = ?, 
        Phone = ?
        WHERE ClientID = ?
    """, (name, address, email, phone, client_id))

    conn.commit()
    rows_updated = cur.rowcount
    conn.close()

    return rows_updated

def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM clients 
        WHERE ClientID = ?
    """, (client_id,))

    conn.commit()
    rows_deleted = cur.rowcount
    conn.close()

    return rows_deleted

# payments
def create_payment(price_total, current_balance):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            INSERT INTO payments (PriceTotal, CurrentBalance)
            VALUES (?, ?)
        """, (price_total, current_balance))
        return cur.lastrowid

def get_payments():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT * FROM payments").fetchall()

def update_payment(payment_id, price_total, current_balance):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            UPDATE payments
            SET PriceTotal = ?,
                CurrentBalance = ?,
                DateUpdated = CURRENT_TIMESTAMP
            WHERE PaymentID = ?
        """, (price_total, current_balance, payment_id))
        return cur.rowcount

def delete_payment(payment_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "DELETE FROM payments WHERE PaymentID = ?",
            (payment_id,)
        )
        return cur.rowcount

# Proposals
def create_proposal(proposal_name, project_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute("""
            INSERT INTO proposals (ProposalName, ProjectID)
            VALUES (?, ?)
        """, (proposal_name, project_id))
        return cur.lastrowid

def get_proposals():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT * FROM proposals").fetchall()

def update_proposal(proposal_id, proposal_name, project_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute("""
            UPDATE proposals
            SET ProposalName = ?,
                ProjectID = ?,
                DateUpdated = CURRENT_TIMESTAMP
            WHERE ProposalID = ?
        """, (proposal_name, project_id, proposal_id))
        return cur.rowcount

def delete_proposal(proposal_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "DELETE FROM proposals WHERE ProposalID = ?",
            (proposal_id,)
        )
        return cur.rowcount

# Reviews
def create_review(reviewer, stars, comments):
    if not 1 <= stars <= 5:
        raise ValueError("Stars must be between 1 and 5")

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            INSERT INTO reviews (Reviewer, Stars, Comments)
            VALUES (?, ?, ?)
        """, (reviewer, stars, comments))
        return cur.lastrowid

def get_reviews():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT * FROM reviews").fetchall()

def update_review(review_id, reviewer, stars, comments):
    if not 1 <= stars <= 5:
        raise ValueError("Stars must be between 1 and 5")

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            UPDATE reviews
            SET Reviewer = ?, Stars = ?, Comments = ?
            WHERE ReviewsID = ?
        """, (reviewer, stars, comments, review_id))
        return cur.rowcount

def delete_review(review_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "DELETE FROM reviews WHERE ReviewsID = ?",
            (review_id,)
        )
        return cur.rowcount

# Skills
SKILL_COLUMNS = (
    "Carpenter",
    "Mechanic",
    "Streamer",
    "Plumber",
    "Consultant",
    "Therapist",
    "Salesman",
    "Engineer",
    "Chef",
    "Manager",
    "HumanResources"
)

def create_skills(skills):
    values = [int(bool(skills.get(skill, 0))) for skill in SKILL_COLUMNS]

    columns = ", ".join(SKILL_COLUMNS)
    placeholders = ", ".join(["?"] * len(SKILL_COLUMNS))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            f"INSERT INTO skillsList ({columns}) VALUES ({placeholders})",
            values
        )
        return cur.lastrowid

def get_skills():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT * FROM skillsList").fetchall()

def update_skills(skills_id, skills):
    values = [int(bool(skills.get(skill, 0))) for skill in SKILL_COLUMNS]

    assignments = ", ".join(
        f"{skill} = ?" for skill in SKILL_COLUMNS
    )

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            f"UPDATE skillsList SET {assignments} WHERE SkillsListID = ?",
            (*values, skills_id)
        )
        return cur.rowcount

def delete_skills(skills_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "DELETE FROM skillsList WHERE SkillsListID = ?",
            (skills_id,)
        )
        return cur.rowcount

# Milestones
def create_milestone(milestone_name, percentage_completed=0,
                     date_started=None):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            INSERT INTO milestones (
                MilestoneName, PercentageCompleted, DateStarted
            )
            VALUES (?, ?, ?)
        """, (milestone_name, percentage_completed, date_started))
        return cur.lastrowid

def get_milestones():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT * FROM milestones").fetchall()

def update_milestone(milestone_id, milestone_name,
                     percentage_completed, date_started):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("""
            UPDATE milestones
            SET MilestoneName = ?,
                PercentageCompleted = ?,
                DateStarted = ?,
                DateUpdated = CURRENT_TIMESTAMP
            WHERE MilestonesID = ?
        """, (milestone_name, percentage_completed,
              date_started, milestone_id))
        return cur.rowcount

def delete_milestone(milestone_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.execute(
            "DELETE FROM milestones WHERE MilestonesID = ?",
            (milestone_id,)
        )
        return cur.rowcount

