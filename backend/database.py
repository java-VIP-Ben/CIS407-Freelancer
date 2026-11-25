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
from contextlib import contextmanager
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

    cur.execute("SELECT FreelancerID, Name, SkillsListID, Email, Phone, ReviewsID FROM freelancers")
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

    cur.execute("SELECT ProjectID, FreelancerID, ClientID, PaymentID, SkillsID, MilestonesID, ProposalID FROM projects")
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

    cur.execute("SELECT ClientID, Name, Address, Phone, Email FROM clients")
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
        return conn.execute("SELECT ProposalID, ProposalName, ProjectID, DateCreated, DateUpdated FROM proposals").fetchall()

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


# Project/proposal interfaces required by the latest frontend.
@contextmanager
def workflow_connection():
    conn = sqlite3.connect(Path(DB_NAME).resolve().as_uri() + '?mode=rw', uri=True, timeout=5)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_project_workflow():
    """Non-destructive migration for named projects and freelancer invitations."""
    with workflow_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        for table, column, definition in (
            ('projects', 'ProjectName', 'TEXT'),
            ('proposals', 'FreelancerID', 'INTEGER REFERENCES freelancers(FreelancerID)'),
            ('proposals', 'PriceCents', "INTEGER CHECK(PriceCents IS NULL OR (typeof(PriceCents) = 'integer' AND PriceCents BETWEEN 0 AND 999999999))"),
            ('proposals', 'Status', "TEXT NOT NULL DEFAULT 'pending' CHECK(Status IN ('pending','accepted','declined'))"),
        ):
            columns = {row[1].lower() for row in conn.execute(f'PRAGMA table_info({table})')}
            if not columns:
                raise ValueError(f'Missing {table} table.')
            if column.lower() not in columns:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {definition}')


def create_client_project(client_id, project_name):
    name = project_name.strip()
    if not name or len(name) > 120:
        raise ValueError('Enter a project name (1–120 characters).')
    with workflow_connection() as conn:
        if client_id is None or not conn.execute('SELECT 1 FROM clients WHERE ClientID=?', (client_id,)).fetchone():
            raise ValueError('A valid client account is required.')
        return conn.execute('INSERT INTO projects (ClientID, ProjectName) VALUES (?, ?)', (client_id, name)).lastrowid


def get_projects_for_client(client_id, include_price=False):
    with workflow_connection() as conn:
        price = ', r.PriceCents' if include_price else ''
        return conn.execute(f'''SELECT p.ProjectID, p.ProjectName, f.Name, p.FreelancerID{price}
            FROM projects p LEFT JOIN freelancers f ON f.FreelancerID=p.FreelancerID
            LEFT JOIN proposals r ON r.ProposalID=p.ProposalID AND r.ProjectID=p.ProjectID AND r.Status='accepted' AND r.FreelancerID=p.FreelancerID
            WHERE p.ClientID=? ORDER BY p.ProjectID DESC''', (client_id,)).fetchall()


def get_projects_for_freelancer(freelancer_id, include_price=False):
    with workflow_connection() as conn:
        price = ', r.PriceCents' if include_price else ''
        return conn.execute(f'''SELECT p.ProjectID, p.ProjectName, p.ClientID, c.Name{price}
            FROM projects p LEFT JOIN clients c ON c.ClientID=p.ClientID
            LEFT JOIN proposals r ON r.ProposalID=p.ProposalID AND r.ProjectID=p.ProjectID AND r.Status='accepted' AND r.FreelancerID=p.FreelancerID
            WHERE p.FreelancerID=? ORDER BY p.ProjectID DESC''', (freelancer_id,)).fetchall()


def create_project_proposal(project_id, freelancer_id, client_id, *, listing_id=None, expected_price_cents=None):
    with workflow_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        project = conn.execute('SELECT ProjectName FROM projects WHERE ProjectID=? AND ClientID=?', (project_id, client_id)).fetchone()
        if project is None:
            raise ValueError('Project does not belong to this client.')
        if freelancer_id is None or not conn.execute('SELECT 1 FROM freelancers WHERE FreelancerID=?', (freelancer_id,)).fetchone():
            raise ValueError('Freelancer does not exist.')
        if conn.execute("SELECT 1 FROM proposals WHERE ProjectID=? AND FreelancerID=? AND Status='pending'", (project_id, freelancer_id)).fetchone():
            raise ValueError('A pending invitation already exists for this freelancer.')
        price = None
        if listing_id is not None:
            listing = conn.execute('SELECT FreelancerID, PriceCents FROM listings WHERE ListingID=?', (listing_id,)).fetchone()
            if listing is None or listing[0] != freelancer_id:
                raise ValueError('Listing no longer exists or has changed freelancer. Refresh Home.')
            price = listing[1]
            if price is None:
                raise ValueError('This listing has no price. Ask the administrator to set one.')
            if type(expected_price_cents) is not int or price != expected_price_cents:
                raise ValueError('The listing price has changed. Close this dialog and refresh Home.')
        elif expected_price_cents is not None:
            raise ValueError('A listing is required to quote a price.')
        return conn.execute('''INSERT INTO proposals (ProposalName, ProjectID, FreelancerID, Status, PriceCents)
            VALUES (?, ?, ?, 'pending', ?)''', (project[0] or f'Project #{project_id}', project_id, freelancer_id, price)).lastrowid


def get_freelancer_proposals(freelancer_id, include_price=False):
    with workflow_connection() as conn:
        price = ', r.PriceCents' if include_price else ''
        return conn.execute(f'''SELECT r.ProposalID, r.ProposalName, p.ProjectID, p.ProjectName,
            p.ClientID, c.Name, r.Status{price} FROM proposals r JOIN projects p ON p.ProjectID=r.ProjectID
            LEFT JOIN clients c ON c.ClientID=p.ClientID WHERE r.FreelancerID=? ORDER BY r.ProposalID DESC''', (freelancer_id,)).fetchall()


def respond_to_project_proposal(proposal_id, freelancer_id, accept):
    with workflow_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute("SELECT ProjectID FROM proposals WHERE ProposalID=? AND FreelancerID=? AND Status='pending'", (proposal_id, freelancer_id)).fetchone()
        if row is None or row[0] is None:
            return 0
        conn.execute('UPDATE proposals SET Status=?, DateUpdated=CURRENT_TIMESTAMP WHERE ProposalID=?', ('accepted' if accept else 'declined', proposal_id))
        if accept:
            conn.execute('UPDATE projects SET FreelancerID=?, ProposalID=? WHERE ProjectID=?', (freelancer_id, proposal_id, row[0]))
        return 1
