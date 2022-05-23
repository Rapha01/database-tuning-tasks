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
		c.execute('DROP TABLE IF EXISTS Accounts')
		c.execute('''CREATE TABLE Accounts (account INT, balance INT)''')
	conn.commit()

def fill_tables(conn):
	with open(path.join(DATA_PATH, 'data.tsv'), 'r', encoding="utf-8") as file, conn.cursor() as c:
		c.copy_from(file, 'Accounts')
	conn.commit()

def table_entries(conn, table: str) -> int:
	with conn.cursor() as c:
		c.execute('SELECT COUNT(*) AS count FROM ' + table)
		res = c.fetchone()
		if res is None:
			raise Exception('empty response for count')
		else:
			return res[0]
