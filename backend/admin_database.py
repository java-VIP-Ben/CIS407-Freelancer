"""Generic CRUD for the eight marketplace tables; no schema changes."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / 'freelancerApp.db'
TABLES = ('freelancers', 'clients', 'projects', 'payments', 'proposals',
          'reviews', 'skillsList', 'milestones')


def quote(identifier):
    """Quote a schema identifier, not a user-supplied SQL value."""
    return '"' + identifier.replace('"', '""') + '"'


def check_table(table):
    if table not in TABLES:
        raise ValueError(f'Unknown admin table: {table}')
    return quote(table)


@contextmanager
def connection():
    # mode=rw prevents creating an empty database at an incorrect path.
    conn = sqlite3.connect(Path(DB_NAME).resolve().as_uri() + '?mode=rw',
                           uri=True, timeout=5)
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


def _schema(conn, table):
    name = check_table(table)
    columns = [dict(row) for row in conn.execute(f'PRAGMA table_info({name})')]
    if not columns:
        raise ValueError(f'Table {table} does not exist in the database.')
    keys = [col for col in columns if col['pk']]
    if len(keys) != 1 or keys[0]['type'].upper() != 'INTEGER':
        raise ValueError(f'{table} must have a single INTEGER primary key.')
    # INTEGER PRIMARY KEY normally aliases SQLite's generated rowid.
    foreign_keys = [dict(row) for row in conn.execute(f'PRAGMA foreign_key_list({name})')]
    return {'columns': columns, 'primary_key': keys[0]['name'],
            'foreign_keys': foreign_keys}


def get_schema(table):
    with connection() as conn:
        return _schema(conn, table)


def get_records(table):
    with connection() as conn:
        schema = _schema(conn, table)
        return [dict(row) for row in conn.execute(
            f'SELECT * FROM {check_table(table)} ORDER BY {quote(schema["primary_key"])}')]


def _values(schema, values):
    editable = {col['name'] for col in schema['columns'] if not col['pk']}
    if set(values) - editable:
        raise ValueError('Unknown column or attempt to edit the primary key.')
    return list(values), list(values.values())


def create_record(table, values):
    """Return the newly inserted record ID. Missing fields use SQL defaults."""
    with connection() as conn:
        schema = _schema(conn, table)
        columns, params = _values(schema, values)
        name = check_table(table)
        if columns:
            names = ', '.join(map(quote, columns))
            placeholders = ', '.join('?' for _ in columns)
            cursor = conn.execute(f'INSERT INTO {name} ({names}) VALUES ({placeholders})', params)
        else:
            cursor = conn.execute(f'INSERT INTO {name} DEFAULT VALUES')
        return cursor.lastrowid


def update_record(table, record_id, values):
    """Return the number of matched rows. Primary keys are never edited."""
    with connection() as conn:
        schema = _schema(conn, table)
        columns, params = _values(schema, values)
        if not columns:
            raise ValueError('No fields to update.')
        assignments = ', '.join(f'{quote(col)} = ?' for col in columns)
        cursor = conn.execute(
            f'UPDATE {check_table(table)} SET {assignments} '
            f'WHERE {quote(schema["primary_key"])} = ?', [*params, record_id])
        return cursor.rowcount


def delete_record(table, record_id):
    """Return the number of deleted rows; respect existing foreign keys."""
    with connection() as conn:
        schema = _schema(conn, table)
        cursor = conn.execute(
            f'DELETE FROM {check_table(table)} WHERE {quote(schema["primary_key"])} = ?',
            (record_id,))
        return cursor.rowcount
