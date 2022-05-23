import psycopg2
from os import path

HOST = 'localhost'
DBNAME = 'postgres'
USER = 'postgres'
PASS = 'pass1234'

DATA_PATH = 'data'

def connect():
    return psycopg2.connect(dbname=DBNAME, user=USER, password=PASS, host=HOST)

def reset_tables(conn):
    with conn.cursor() as c:
        c.execute('DROP TABLE IF EXISTS publ')
        c.execute('''CREATE TABLE publ (
            pubID       CHAR(149),
            type        CHAR(13),
            title       CHAR(700),
            booktitle   CHAR(132),
            year        CHAR(4),
            publisher   CHAR(196)
            )''')

        c.execute('DROP TABLE IF EXISTS auth')
        c.execute('''CREATE TABLE auth (
            name        CHAR(49),
            pubID       CHAR(149)
            )''')
    conn.commit()

def fill_tables(conn):
    with open(path.join(DATA_PATH, 'publ.tsv'), 'r', encoding="utf-8") as file, conn.cursor() as c:
        c.copy_from(file, 'publ')

    # we don't need AUTH
    # with open(path.join(DATA_PATH, 'auth.tsv'), 'r', encoding="utf-8") as file, conn.cursor() as c:
    #     c.copy_from(file, 'auth')
    conn.commit()

def table_entries(conn, table: str) -> int:
    with conn.cursor() as c:
        c.execute('SELECT COUNT(*) AS count FROM ' + table)
        res = c.fetchone()
        if res is None:
            raise Exception('empry response for count')
        else:
            return res[0]
