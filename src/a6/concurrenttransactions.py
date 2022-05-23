from concurrent.futures import ThreadPoolExecutor, wait
import psycopg2, db, sys, traceback
from time import perf_counter

def _extractInt(cursor):
	return int(cursor.fetchall()[-1][0])

def TransactionA(conn, account, isolation_level):
	conn.set_session(isolation_level = isolation_level)
	with conn.cursor() as c:
		c.execute('SELECT balance FROM Accounts WHERE account=' + str(account))
		e = _extractInt(c)
		c.execute('UPDATE Accounts SET balance=' + str(e+1) + ' WHERE account=' + str(account))
		c.execute('SELECT balance FROM Accounts WHERE account=0')
		b = _extractInt(c)
		c.execute('UPDATE Accounts SET balance=' + str(b-1) + ' WHERE account=0')
		conn.commit()

def TransactionB(conn, account, isolation_level):
	conn.set_session(isolation_level = isolation_level)
	with conn.cursor() as c:
		c.execute('UPDATE Accounts SET balance=balance+1 WHERE account=' + str(account))
		c.execute('UPDATE Accounts SET balance=balance-1 WHERE account=0')
		conn.commit()

# runs a transaction until it passes
def _runTransaction(transaction, account, isolation_level):
	done = False
	with db.connect() as conn: # use a connection per thread
		while not done:
			try:
				transaction(conn, account, isolation_level)
				done = True
			except:
				conn.rollback()

def _companyBalance(conn) -> int:
	with conn.cursor() as c:
		c.execute("SELECT balance FROM Accounts WHERE account='0'")
		return int(c.fetchall()[-1][0])

def stringTable(conn) -> str:
	with conn.cursor() as c:
		c.execute("SELECT * FROM Accounts")
		return 'acc_id, balance\n' + '\n'.join(map(lambda el: str(el[0]) + ', ' + str(el[1]), c.fetchall()))

# maxconcurrent = max. parallel working threads
# transaction = transaction function
def _startThreadPoolWorking(maxconcurrent, transaction, isolation_level):
	with ThreadPoolExecutor(max_workers=maxconcurrent) as executor:
		futures={executor.submit(_runTransaction, transaction, i, isolation_level): i for i in range(1,101)}
		wait(futures)

# returns throughput, correctness
def measureTransaction(conn, maxconcurrent, transaction, isolation_level) -> (float, float):
	c1 = _companyBalance(conn)
	start = perf_counter()
	_startThreadPoolWorking(maxconcurrent, transaction, isolation_level)
	diff = perf_counter() - start
	c2 = _companyBalance(conn)
	# print(stringTable(conn))
	return 100/diff, (c1-c2)/100
