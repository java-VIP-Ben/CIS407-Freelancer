"""Password authentication for existing client and freelancer records."""
import argparse
import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import contextmanager
from getpass import getpass
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / 'freelancerApp.db'
ITERATIONS = 600_000
ACCOUNTS = {'client': ('clients', 'ClientID'), 'freelancer': ('freelancers', 'FreelancerID')}

@contextmanager
def connection():
    conn = sqlite3.connect(Path(DB_NAME).resolve().as_uri() + '?mode=rw', uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_auth():
    """Add password fields, leaving existing IDs, emails and data unchanged."""
    with connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        for table, pk in ACCOUNTS.values():
            columns = {row['name'].lower() for row in conn.execute(f'PRAGMA table_info({table})')}
            if not {pk.lower(), 'name', 'email'} <= columns:
                raise ValueError(f'Missing required columns in {table}.')
            if 'passwordhash' not in columns:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN PasswordHash TEXT')
            conn.execute(f'''CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_active_email
                ON {table}(lower(trim(Email))) WHERE PasswordHash IS NOT NULL''')
            # Keep legacy duplicates, but never introduce a collision with an active account.
            for action in ('INSERT', 'UPDATE OF Email, PasswordHash'):
                suffix = 'insert' if action == 'INSERT' else 'update'
                exclude = '' if action == 'INSERT' else f'AND {pk} <> OLD.{pk}'
                conn.execute(f'''CREATE TRIGGER IF NOT EXISTS auth_{table}_{suffix}
                    BEFORE {action} ON {table}
                    WHEN (NEW.PasswordHash IS NOT NULL AND
                          (NEW.Email IS NULL OR trim(NEW.Email) = ''))
                      OR EXISTS (SELECT 1 FROM {table}
                        WHERE lower(trim(Email)) = lower(trim(NEW.Email)) {exclude}
                        AND (PasswordHash IS NOT NULL OR NEW.PasswordHash IS NOT NULL))
                    BEGIN SELECT RAISE(ABORT, 'Active accounts require unique nonempty emails'); END''')


def normalize_email(email):
    email = email.strip().lower()
    if not email.isascii() or len(email) > 254 or email.count('@') != 1 or any(c.isspace() for c in email):
        raise ValueError('Enter a valid email address.')
    local, domain = email.split('@')
    if not local or '.' not in domain or not all(domain.split('.')):
        raise ValueError('Enter a valid email address.')
    return email


def hash_password(password):
    if not 12 <= len(password) <= 1024:
        raise ValueError('Use a password between 12 and 1024 characters.')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
    return f'pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}'


def verify_password(password, encoded):
    if not encoded or len(password) > 1024:
        return False
    try:
        algorithm, rounds, salt, digest = encoded.split('$')
        if algorithm != 'pbkdf2_sha256' or int(rounds) != ITERATIONS:
            return False
        salt, expected = bytes.fromhex(salt), bytes.fromhex(digest)
        if len(salt) != 16 or len(expected) != 32:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, AttributeError):
        return False


def register_client(name, email, address, phone, password):
    name, address, phone = name.strip(), address.strip(), phone.strip()
    if not name or len(name) > 50 or not address or not phone:
        raise ValueError('Enter name (up to 50 characters), address and phone.')
    email = normalize_email(email)
    encoded = hash_password(password)
    initialize_auth()
    with connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute('SELECT 1 FROM clients WHERE lower(trim(Email)) = ?', (email,)).fetchone():
            raise ValueError('Email already belongs to a client. Ask the administrator to activate your account.')
        return conn.execute('''INSERT INTO clients (Name, Email, Address, Phone, PasswordHash)
            VALUES (?, ?, ?, ?, ?)''', (name, email, address, phone, encoded)).lastrowid


def authenticate_account(role, email, password):
    table, pk = ACCOUNTS[role]
    try:
        email = normalize_email(email)
    except ValueError:
        return None
    initialize_auth()
    with connection() as conn:
        rows = conn.execute(f'''SELECT {pk}, Name, Email, PasswordHash FROM {table}
            WHERE lower(trim(Email)) = ? LIMIT 2''', (email,)).fetchall()
    if len(rows) != 1 or not verify_password(password, rows[0]['PasswordHash']):
        return None
    return {key: rows[0][key] for key in (pk, 'Name', 'Email')}


def authenticate_client(email, password):
    return authenticate_account('client', email, password)


def authenticate_freelancer(email, password):
    return authenticate_account('freelancer', email, password)


def authenticate_admin(username, password):
    return username == "admin" and password == "admin"


def set_account_password(role, account_id, password):
    table, pk = ACCOUNTS[role]
    encoded = hash_password(password)
    initialize_auth()
    with connection() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute(f'SELECT Email FROM {table} WHERE {pk} = ?', (account_id,)).fetchone()
        if row is None:
            raise ValueError('Account ID not found.')
        email = normalize_email(row['Email'] or '')
        if conn.execute(f'SELECT 1 FROM {table} WHERE lower(trim(Email)) = ? AND {pk} <> ?', (email, account_id)).fetchone():
            raise ValueError('Duplicate email. Assign distinct emails in Admin before activating.')
        conn.execute(f'UPDATE {table} SET PasswordHash = ? WHERE {pk} = ?', (encoded, account_id))


def set_client_password(client_id, password):
    set_account_password('client', client_id, password)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize login or activate an existing account.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--set-password', type=int, metavar='CLIENT_ID')
    group.add_argument('--set-freelancer-password', type=int, metavar='FREELANCER_ID')
    args = parser.parse_args()
    try:
        initialize_auth()
        from backend.database import initialize_project_workflow
        initialize_project_workflow()
        if args.set_password is not None or args.set_freelancer_password is not None:
            pw = getpass('New password: ')
            if pw != getpass('Confirm password: '):
                raise ValueError('Passwords do not match.')
            role = 'client' if args.set_password is not None else 'freelancer'
            account_id = args.set_password if role == 'client' else args.set_freelancer_password
            set_account_password(role, account_id, pw)
            print('Password set.')
        else:
            print('Account and project workflow schemas ready.')
    except (sqlite3.Error, ValueError) as exc:
        parser.exit(1, f'Error: {exc}\n')
