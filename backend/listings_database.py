"""Non-destructive listing migration, CRUD, and search for the marketplace."""
import sqlite3
import re
from decimal import Decimal
from contextlib import contextmanager
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / "freelancerApp.db"
SEARCH_FIELDS = {
    "All fields": ("Name", "JobTitle", "Description", "Skills", "Category"),
    "Freelancer name": ("Name",),
    "Job / title": ("JobTitle",),
    "Description": ("Description",),
    "Skills": ("Skills",),
    "Category": ("Category",),
}


@contextmanager
def connection():
    # Never silently create a new database if the real database is missing.
    conn = sqlite3.connect(Path(DB_NAME).resolve().as_uri() + "?mode=rw",
                           uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_listings():
    """Create just the new table. Safe to run repeatedly; no DROP statements."""
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        # Check the existing parent table before attempting the migration.
        conn.execute("SELECT FreelancerID, Name FROM freelancers LIMIT 0")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                ListingID INTEGER PRIMARY KEY AUTOINCREMENT,
                FreelancerID INTEGER NOT NULL,
                JobTitle TEXT NOT NULL CHECK(length(trim(JobTitle)) > 0),
                Description TEXT NOT NULL CHECK(length(trim(Description)) > 0),
                Skills TEXT NOT NULL CHECK(length(trim(Skills)) > 0),
                Category TEXT NOT NULL DEFAULT '',
                CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PriceCents INTEGER CHECK(PriceCents IS NULL OR (typeof(PriceCents) = 'integer' AND PriceCents BETWEEN 0 AND 999999999)),
                FOREIGN KEY (FreelancerID) REFERENCES freelancers(FreelancerID)
                    ON DELETE RESTRICT
            )
        """)
        columns = {row[1].lower() for row in conn.execute("PRAGMA table_info(listings)")}
        if "pricecents" not in columns:
            conn.execute("ALTER TABLE listings ADD COLUMN PriceCents INTEGER CHECK(PriceCents IS NULL OR (typeof(PriceCents) = 'integer' AND PriceCents BETWEEN 0 AND 999999999))")
        # Report an incompatible pre-existing table instead of overwriting it.
        conn.execute("SELECT ListingID, FreelancerID, JobTitle, Description, Skills, Category, CreatedAt FROM listings LIMIT 0")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_freelancer ON listings(FreelancerID)")


def get_freelancer_options():
    with connection() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT FreelancerID, Name FROM freelancers ORDER BY Name COLLATE NOCASE, FreelancerID"
        )]


def get_listings():
    """Join names from the parent table so name changes appear automatically."""
    with connection() as conn:
        review_tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name IN ('freelancer_reviews', 'reviews')"
            )
        }
        has_reviews = {'freelancer_reviews', 'reviews'} <= review_tables
        review_stats = """
            LEFT JOIN (
                SELECT fr.FreelancerID, ROUND(AVG(r.Stars), 1) AS AverageRating,
                       COUNT(*) AS ReviewCount
                FROM freelancer_reviews fr
                JOIN reviews r ON r.ReviewsID=fr.ReviewsID
                GROUP BY fr.FreelancerID
            ) ratings ON ratings.FreelancerID=f.FreelancerID
        """ if has_reviews else ""
        rating_columns = (
            "ratings.AverageRating, COALESCE(ratings.ReviewCount, 0) AS ReviewCount"
            if has_reviews else "NULL AS AverageRating, 0 AS ReviewCount"
        )
        return [dict(row) for row in conn.execute("""
            SELECT l.ListingID, l.FreelancerID, f.Name, l.JobTitle,
                   l.Description, l.Skills, l.Category, l.CreatedAt, l.PriceCents,
                   {rating_columns}
            FROM listings AS l
            JOIN freelancers AS f ON f.FreelancerID = l.FreelancerID
            {review_stats}
            ORDER BY l.ListingID DESC
        """.format(rating_columns=rating_columns, review_stats=review_stats))]


def get_listings_for_freelancer(freelancer_id):
    if not isinstance(freelancer_id, int) or isinstance(freelancer_id, bool):
        raise ValueError("Select a freelancer.")
    with connection() as conn:
        return [dict(row) for row in conn.execute("""
            SELECT l.ListingID, l.FreelancerID, f.Name, l.JobTitle,
                   l.Description, l.Skills, l.Category, l.CreatedAt, l.PriceCents
            FROM listings AS l
            JOIN freelancers AS f ON f.FreelancerID = l.FreelancerID
            WHERE l.FreelancerID = ?
            ORDER BY l.ListingID DESC
        """, (freelancer_id,))]


def filter_listings(rows, query="", field="All fields"):
    """Literal, Unicode-aware, case-insensitive matching. All words must match."""
    if field not in SEARCH_FIELDS:
        raise ValueError("Unknown search field.")
    words = query.casefold().split()
    columns = SEARCH_FIELDS[field]
    return [row for row in rows if all(
        any(word in str(row.get(column) or "").casefold() for column in columns)
        for word in words
    )]


def search_listings(query="", field="All fields"):
    return filter_listings(get_listings(), query, field)


def _validate(freelancer_id, job_title, description, skills, category):
    if not isinstance(freelancer_id, int) or isinstance(freelancer_id, bool):
        raise ValueError("Select a freelancer.")
    fields = []
    for label, value, limit, required in (
        ("Job title", job_title, 120, True),
        ("Description", description, 4000, True),
        ("Skills", skills, 500, True),
        ("Category", category, 80, False),
    ):
        if not isinstance(value, str):
            raise ValueError(f"{label} must be text.")
        value = value.strip()
        if required and not value:
            raise ValueError(f"{label} is required.")
        if len(value) > limit:
            raise ValueError(f"{label} must be {limit} characters or fewer.")
        fields.append(value)
    return (freelancer_id, *fields)


def parse_price(text):
    """Convert a decimal USD amount to exact integer cents."""
    text = text.strip()
    if not re.fullmatch(r"[0-9]{1,7}(?:\.[0-9]{1,2})?", text):
        raise ValueError("Enter a price in USD (for example 125.50), with at most two decimal places.")
    cents = int(Decimal(text) * 100)
    return validate_price_cents(cents)


def validate_price_cents(cents):
    if type(cents) is not int or not 0 <= cents <= 999999999:
        raise ValueError("Price must be between $0.00 and $9,999,999.99.")
    return cents


def format_price(cents):
    if cents is None:
        return "Price not set"
    return f"${cents // 100:,}.{cents % 100:02d}"


def create_listing(freelancer_id, job_title, description, skills, category="", price_cents=None):
    values = _validate(freelancer_id, job_title, description, skills, category)
    with connection() as conn:
        cursor = conn.execute("""
            INSERT INTO listings (FreelancerID, JobTitle, Description, Skills, Category, PriceCents)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (*values, None if price_cents is None else validate_price_cents(price_cents)))
        return cursor.lastrowid


def update_listing(listing_id, freelancer_id, job_title, description, skills, category="", price_cents=None):
    values = _validate(freelancer_id, job_title, description, skills, category)
    with connection() as conn:
        cursor = conn.execute("""
            UPDATE listings SET FreelancerID = ?, JobTitle = ?, Description = ?,
                                Skills = ?, Category = ?, PriceCents = COALESCE(?, PriceCents) WHERE ListingID = ?
        """, (*values, None if price_cents is None else validate_price_cents(price_cents), listing_id))
        return cursor.rowcount


def update_listing_for_freelancer(listing_id, freelancer_id, job_title, description, skills, category="", price_cents=None):
    values = _validate(freelancer_id, job_title, description, skills, category)
    with connection() as conn:
        cursor = conn.execute("""
            UPDATE listings SET JobTitle = ?, Description = ?, Skills = ?,
                                Category = ?, PriceCents = COALESCE(?, PriceCents)
            WHERE ListingID = ? AND FreelancerID = ?
        """, (*values[1:], None if price_cents is None else validate_price_cents(price_cents),
              listing_id, freelancer_id))
        return cursor.rowcount


def delete_listing(listing_id):
    with connection() as conn:
        return conn.execute("DELETE FROM listings WHERE ListingID = ?", (listing_id,)).rowcount


def delete_listing_for_freelancer(listing_id, freelancer_id):
    if not isinstance(freelancer_id, int) or isinstance(freelancer_id, bool):
        raise ValueError("Select a freelancer.")
    with connection() as conn:
        return conn.execute(
            "DELETE FROM listings WHERE ListingID = ? AND FreelancerID = ?",
            (listing_id, freelancer_id),
        ).rowcount


if __name__ == "__main__":
    initialize_listings()
    print("Listings table is ready. Existing tables and records were preserved.")
