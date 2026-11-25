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


from datetime import datetime
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
        milestone_columns = {
            row[1].lower() for row in conn.execute('PRAGMA table_info(milestones)')
        }
        project_columns = {
            row[1].lower() for row in conn.execute('PRAGMA table_info(projects)')
        }
        if milestone_columns and {'projectid', 'milestonesid'} <= project_columns:
            conn.execute('''CREATE TABLE IF NOT EXISTS project_milestones (
                ProjectID INTEGER NOT NULL REFERENCES projects(ProjectID) ON DELETE CASCADE,
                MilestonesID INTEGER NOT NULL REFERENCES milestones(MilestonesID) ON DELETE CASCADE,
                PRIMARY KEY (ProjectID, MilestonesID)
            )''')
            conn.execute('''INSERT OR IGNORE INTO project_milestones (ProjectID, MilestonesID)
                SELECT p.ProjectID, p.MilestonesID FROM projects p
                JOIN milestones m ON m.MilestonesID=p.MilestonesID
                WHERE p.MilestonesID IS NOT NULL''')
        review_columns = {
            row[1].lower() for row in conn.execute('PRAGMA table_info(reviews)')
        }
        if (
            'reviewsid' in review_columns
            and {'projectid', 'clientid', 'freelancerid'} <= project_columns
            and conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='clients'"
            ).fetchone()
            and conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='freelancers'"
            ).fetchone()
        ):
            conn.execute('''CREATE TABLE IF NOT EXISTS freelancer_reviews (
                ReviewsID INTEGER PRIMARY KEY REFERENCES reviews(ReviewsID) ON DELETE CASCADE,
                ProjectID INTEGER NOT NULL UNIQUE REFERENCES projects(ProjectID) ON DELETE CASCADE,
                ClientID INTEGER NOT NULL REFERENCES clients(ClientID) ON DELETE CASCADE,
                FreelancerID INTEGER NOT NULL REFERENCES freelancers(FreelancerID) ON DELETE CASCADE
            )''')


def create_client_project(client_id, project_name):
    name = project_name.strip()
    if not name or len(name) > 120:
        raise ValueError('Enter a project name (1–120 characters).')
    with workflow_connection() as conn:
        if client_id is None or not conn.execute('SELECT 1 FROM clients WHERE ClientID=?', (client_id,)).fetchone():
            raise ValueError('A valid client account is required.')
        return conn.execute('INSERT INTO projects (ClientID, ProjectName) VALUES (?, ?)', (client_id, name)).lastrowid


def update_client_project(client_id, project_id, project_name):
    if not isinstance(project_name, str):
        raise ValueError('Enter a project name (1–120 characters).')
    name = project_name.strip()
    if not name or len(name) > 120:
        raise ValueError('Enter a project name (1–120 characters).')
    with workflow_connection() as conn:
        cursor = conn.execute(
            'UPDATE projects SET ProjectName=? WHERE ProjectID=? AND ClientID=?',
            (name, project_id, client_id),
        )
        return cursor.rowcount


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


def _validate_milestone_progress(progress):
    if isinstance(progress, bool) or not isinstance(progress, (int, float)):
        raise ValueError('Milestone progress must be a number from 0 to 100.')
    if not 0 <= progress <= 100:
        raise ValueError('Milestone progress must be between 0 and 100.')
    return float(progress)


def get_project_summaries(role, account_id):
    project_owner = {'client': 'ClientID', 'freelancer': 'FreelancerID'}.get(role)
    if project_owner is None:
        raise ValueError('Invalid account role.')
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise ValueError('A valid account is required.')
    with workflow_connection() as conn:
        rows = conn.execute(f'''SELECT p.ProjectID, p.ProjectName, p.FreelancerID,
                f.Name, m.MilestonesID, m.MilestoneName,
                m.PercentageCompleted, m.DateStarted
            FROM projects p
            LEFT JOIN freelancers f ON f.FreelancerID=p.FreelancerID
            LEFT JOIN project_milestones pm ON pm.ProjectID=p.ProjectID
            LEFT JOIN milestones m ON m.MilestonesID=pm.MilestonesID
            WHERE p.{project_owner}=?
            ORDER BY p.ProjectID DESC, m.MilestonesID''', (account_id,)).fetchall()
    projects = {}
    for (project_id, name, freelancer_id, freelancer_name, milestone_id,
         milestone_name, progress, date_started) in rows:
        project = projects.setdefault(project_id, {
            'ProjectID': project_id, 'ProjectName': name,
            'FreelancerID': freelancer_id, 'FreelancerName': freelancer_name,
            'Milestones': [], 'Progress': 0,
        })
        if milestone_id is not None:
            percentage = _validate_milestone_progress(
                progress if progress is not None else 0
            )
            project['Milestones'].append({
                'MilestonesID': milestone_id,
                'MilestoneName': milestone_name,
                'PercentageCompleted': percentage,
                'DateStarted': date_started,
            })
    for project in projects.values():
        milestones = project['Milestones']
        if milestones:
            project['Progress'] = round(
                sum(item['PercentageCompleted'] for item in milestones) / len(milestones)
            )
    return list(projects.values())


def get_project_review(project_id, role, account_id):
    project_owner = {'client': 'ClientID', 'freelancer': 'FreelancerID'}.get(role)
    if project_owner is None:
        raise ValueError('Invalid account role.')
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise ValueError('A valid account is required.')
    with workflow_connection() as conn:
        row = conn.execute(f'''SELECT r.ReviewsID, r.Reviewer, r.Stars, r.Comments
            FROM projects p
            JOIN freelancer_reviews fr ON fr.ProjectID=p.ProjectID
            JOIN reviews r ON r.ReviewsID=fr.ReviewsID
            WHERE p.ProjectID=? AND p.{project_owner}=?''',
            (project_id, account_id)).fetchone()
    if row is None:
        return None
    return {
        'ReviewsID': row[0],
        'Reviewer': row[1],
        'Stars': row[2],
        'Comments': row[3],
    }


def create_freelancer_review(client_id, project_id, stars, comments):
    if type(stars) is not int or not 1 <= stars <= 5:
        raise ValueError('Choose a rating from 1 to 5 stars.')
    if not isinstance(comments, str):
        raise ValueError('Review comments must be text.')
    comments = comments.strip()
    if len(comments) > 2000:
        raise ValueError('Review comments must be 2000 characters or fewer.')
    with workflow_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        project = conn.execute('''SELECT p.FreelancerID, c.Name
            FROM projects p JOIN clients c ON c.ClientID=p.ClientID
            WHERE p.ProjectID=? AND p.ClientID=? AND p.FreelancerID IS NOT NULL''',
            (project_id, client_id)).fetchone()
        if project is None:
            raise ValueError('Only a client on a project with an assigned freelancer can leave a review.')
        if conn.execute(
            'SELECT 1 FROM freelancer_reviews WHERE ProjectID=?', (project_id,)
        ).fetchone():
            raise ValueError('A review has already been submitted for this project.')
        reviewer = project[1] or f'Client #{client_id}'
        review_id = conn.execute('''INSERT INTO reviews (Reviewer, Stars, Comments)
            VALUES (?, ?, ?)''', (reviewer, stars, comments)).lastrowid
        conn.execute('''INSERT INTO freelancer_reviews
            (ReviewsID, ProjectID, ClientID, FreelancerID) VALUES (?, ?, ?, ?)''',
            (review_id, project_id, client_id, project[0]))
        return review_id


def create_project_milestone(project_id, role, account_id, name, progress=0, date_started=None):
    if role != 'client':
        raise ValueError('Only clients can update project milestones.')
    project_owner = 'ClientID'
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise ValueError('A valid account is required.')
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
        raise ValueError('Enter a milestone name (1–120 characters).')
    progress = _validate_milestone_progress(progress)
    if date_started:
        try:
            datetime.strptime(date_started, '%Y-%m-%d')
        except (TypeError, ValueError):
            raise ValueError('Start date must use YYYY-MM-DD format.') from None
    with workflow_connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if not conn.execute(
            f'SELECT 1 FROM projects WHERE ProjectID=? AND {project_owner}=?',
            (project_id, account_id),
        ).fetchone():
            raise ValueError('Project does not belong to this account.')
        milestone_id = conn.execute('''INSERT INTO milestones
            (MilestoneName, PercentageCompleted, DateStarted) VALUES (?, ?, ?)''',
            (name.strip(), progress, date_started or None)).lastrowid
        conn.execute(
            'INSERT INTO project_milestones (ProjectID, MilestonesID) VALUES (?, ?)',
            (project_id, milestone_id),
        )
        return milestone_id


def update_project_milestone_progress(project_id, milestone_id, role, account_id, progress):
    if role != 'client':
        raise ValueError('Only clients can update project milestones.')
    project_owner = 'ClientID'
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise ValueError('A valid account is required.')
    progress = _validate_milestone_progress(progress)
    with workflow_connection() as conn:
        cursor = conn.execute(f'''UPDATE milestones
            SET PercentageCompleted=?, DateUpdated=CURRENT_TIMESTAMP
            WHERE MilestonesID=? AND EXISTS (
                SELECT 1 FROM project_milestones pm
                JOIN projects p ON p.ProjectID=pm.ProjectID
                WHERE pm.MilestonesID=? AND p.ProjectID=? AND p.{project_owner}=?
            )''', (progress, milestone_id, milestone_id, project_id, account_id))
        return cursor.rowcount


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
