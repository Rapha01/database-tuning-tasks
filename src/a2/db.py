from os import mkdir, getcwd, path
import psycopg2
import random
import string

HOST = 'localhost'
DBNAME = 'postgres'
USER = 'postgres'
PASS = 'admin'

DATA_PATH = 'data'

def connect():
    return psycopg2.connect(dbname=DBNAME, user=USER, password=PASS, host=HOST)

def reset_tables(conn):
    with conn.cursor() as c:
        c.execute('DROP TABLE IF EXISTS employee')
        c.execute('DROP TABLE IF EXISTS student')
        c.execute('DROP TABLE IF EXISTS techdept')
        c.execute('''CREATE TABLE employee (
            ssnum       INT,
            name        VARCHAR(49),
            manager     VARCHAR(49),
            dept        VARCHAR(49),
            salary      INT,
            numfriends  INT
            )''')
        c.execute('CREATE UNIQUE INDEX ON employee (ssnum)')
        c.execute('CREATE UNIQUE INDEX ON employee (name)')
        c.execute('CREATE INDEX ON employee (dept)')
        c.execute('''CREATE TABLE student (
            ssnum       INT,
            name        VARCHAR(49),
            course      VARCHAR(49),
            grade       INT
            )''')
        c.execute('CREATE UNIQUE INDEX ON student (ssnum)')
        c.execute('CREATE UNIQUE INDEX ON student (name)')
        c.execute('''CREATE TABLE techdept (
            dept        VARCHAR(49),
            manager     VARCHAR(49),
            location    VARCHAR(49)
            )''')
        c.execute('CREATE UNIQUE INDEX ON techdept (dept)')
    conn.commit()
    __fill_tables(conn)

def __fill_tables(conn):
    __copy(DATA_PATH+"/employee.tsv", "employee", conn)
    __copy(DATA_PATH+"/student.tsv", "student", conn)
    __copy(DATA_PATH+"/techdept.tsv", "techdept", conn)

def table_entries(conn, table: str) -> int:
    with conn.cursor() as c:
        c.execute('SELECT COUNT(*) AS count FROM ' + table)
        res = c.fetchone()
        if res is None:
            raise Exception('empry response for count')
        else:
            return res[0]

def __copy(data_path, table, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        c.copy_from(file, table)
    conn.commit()
