import psycopg2, db, data_setup, time, re
import concurrenttransactions as ct

def _reset(conn):
	print('resetting tables', end='\r')
	db.reset_tables(conn)
	db.fill_tables(conn)
	print(80*' ', '\r', end='')

def _explain(conn, query:str) -> str:
	with conn.cursor() as c:
		c.execute('EXPLAIN ' + query)
		return '\n'.join(map(lambda el: el[0],c.fetchall()))

def _analyze(cursor, query:str) -> float:
	cursor.execute('EXPLAIN ANALYZE ' + query)
	return float(re.fullmatch(r"^Execution time: (?P<time>\d*\.\d*) ms$", cursor.fetchall()[-1][0]).groupdict()['time'])



if __name__ == '__main__':
	data_setup.run()
	conn = db.connect()

	print('### Transaction A (local temp value) ###')
	print('  > isolation: READ COMMITED')

	for i in range(1,6):
		_reset(conn)
		print('  #threads:', i, 'troughput/correctness', ct.measureTransaction(conn, i, ct.TransactionA, psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED))

	print('  > isolation: SERIALIZABLE')

	for i in range(1,6):
		_reset(conn)
		print('  #threads:', i, 'troughput/correctness', ct.measureTransaction(conn, i, ct.TransactionA, psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE))

	print('### Transaction B (direct update) ###')
	print('  > isolation: READ COMMITED')

	for i in range(1,6):
		_reset(conn)
		print('  #threads:', i, 'troughput/correctness', ct.measureTransaction(conn, i, ct.TransactionB, psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED))

	print('  > isolation: SERIALIZABLE')

	for i in range(1,6):
		_reset(conn)
		print('  #threads:', i, 'troughput/correctness', ct.measureTransaction(conn, i, ct.TransactionB, psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE))
	conn.close()
