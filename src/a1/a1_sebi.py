import psycopg2
import csv
import time


# CONNECT DATABASE
connection = psycopg2.connect(dbname='postgres', user='postgres', password='admin')
cursor = connection.cursor()

def resetTables():
    cursor.execute('DROP TABLE IF EXISTS auth')
    cursor.execute('DROP TABLE IF EXISTS publ')

    cursor.execute('''CREATE TABLE auth (
        name   VARCHAR(49),
        pubID  VARCHAR(129)
        )''')
    cursor.execute('''CREATE TABLE publ (
        pubID     VARCHAR(129),
        type      VARCHAR(13),
        title     VARCHAR(700),
        booktitle VARCHAR(132),
        year      VARCHAR(4),
        publisher VARCHAR(196)
        )''')

def getRowsCount(table):
    cursor.execute('SELECT COUNT(*) AS count FROM ' + table)
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    else:
        return 0


# LOAD DATA
data = [];
with open('auth.tsv', 'r', encoding='utf-8') as f:
    for row in csv.reader(f):
        parts = row[0].split('\t')
        data.append({'name':parts[0],'pubID':parts[1]})


testPercentage = 10
rowLimit = len(data) * (testPercentage / 100)
print('Measuring ' + str(testPercentage) + '% of data')


# APPROACH: Straigtforward
print('Approach: Straigtforward')
resetTables()
startTime = time.time()

for i,row in enumerate(data):
    if (i > rowLimit):
        break
    cursor.execute('INSERT INTO auth (name, pubID) VALUES (%s, %s);', (row['name'], row['pubID']))
    connection.commit()

elapsedTime = time.time() - startTime
print('  Elapsed time ' + str(round(elapsedTime,4)) + 's')
print('  Rows inserted: ', getRowsCount('auth'))


# APPROACH: Straigtforward + One transaction
print('Approach: Straigtforward + One transaction')
resetTables()
startTime = time.time()

for i,row in enumerate(data):
    if (i > rowLimit):
        break
    cursor.execute('INSERT INTO auth (name, pubID) VALUES (%s, %s);', (row['name'], row['pubID']))

elapsedTime = time.time() - startTime
print('  Elapsed time ' + str(round(elapsedTime,4)) + 's')
print('  Rows inserted: ', getRowsCount('auth'))


# APPROACH: Prepared Statements + One transaction
print('Approach: Prepared Statements + One transaction')
resetTables()
cursor.execute('PREPARE authInsert1 (varchar (49) , varchar (129)) AS \
        INSERT INTO auth VALUES ($1 , $2)', data)
startTime = time.time()

for i,row in enumerate(data):
    if (i > rowLimit):
        break
    cursor.execute('EXECUTE authInsert1 (%s, %s);', (row['name'],row['pubID']))

elapsedTime = time.time() - startTime
print('  Elapsed time ' + str(round(elapsedTime,4)) + 's')
print('  Rows inserted: ', getRowsCount('auth'))


# APPROACH: Prepared Statements + One transaction + Multi row insert
print('Approach: Prepared Statements + One transaction + Multi row insert')
resetTables()
startTime = time.time()
cursor.execute('PREPARE authInsert2 (varchar (49) , varchar (129)) AS \
        INSERT INTO auth VALUES ($1 , $2),($3 , $4),($5 , $6),($7 , $8), \
        ($9 , $10),($11 , $12),($13 , $14),($15 , $16),($17 , $18),($19 , $20)', data)

i = 0
while i < len(data):
    if (i > rowLimit - 10):
        break
    cursor.execute('EXECUTE authInsert2 ( \
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', \
            (data[i]['name'],data[i]['pubID'],data[i+1]['name'],data[i+1]['pubID'], \
            data[i+2]['name'],data[i+2]['pubID'],data[i+3]['name'],data[i+3]['pubID'], \
            data[i+4]['name'],data[i+4]['pubID'],data[i+5]['name'],data[i+5]['pubID'], \
            data[i+6]['name'],data[i+6]['pubID'],data[i+7]['name'],data[i+7]['pubID'], \
            data[i+8]['name'],data[i+8]['pubID'],data[i+9]['name'],data[i+9]['pubID']))
    i = i + 10;

elapsedTime = time.time() - startTime
print('  Elapsed time ' + str(round(elapsedTime,4)) + 's')
print('  Rows inserted: ', getRowsCount('auth'))


# CLOSE CONNECTION
connection.commit()
cursor.close()
connection.close()
