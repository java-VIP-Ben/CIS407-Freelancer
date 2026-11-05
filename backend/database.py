import sqlite3

DB_NAME = "freelancerApp.db"

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
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM freelancers
        WHERE FreelancerID = ?
    """, (freelancer_id,))

    conn.commit()
    rows_deleted = cur.rowcount
    conn.close()

    return rows_deleted


