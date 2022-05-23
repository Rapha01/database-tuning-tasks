import psycopg2, db, data_setup, time, re

RUNTIME = 60 # in seconds

pubIDs = [
    'conf/sigcomm/BrakmoOP94',
    'conf/sigcomm/AbbottP92',
    'conf/sigcomm/BrandriffLN85',
    'conf/sigcomm/AbramsSAFW96',
    'conf/sigcomm/BraunD95',
    'conf/sigcomm/AdiseshuPV96',
    'conf/sigcomm/Bremler-BarrAH99',
    'conf/sigcomm/AfekMO96',
    'conf/sigcomm/BrendanTS91',
    'conf/sigcomm/Agre86',
    'conf/ijcnn/LinTY08',
    'conf/ijcnn/PanW08',
    'conf/ijcnn/AlyTTS08',
    'conf/ijcnn/SunWLH08',
    'conf/ijcnn/Liu08'
]
booktitles = [
    'SIGCOMM',
    'VISSAPP',
    'GRAPP',
    'MFPS',
    'IKE',
    'IJCNN',
    'COLING',
    'DS-RT',
    'ESOP',
    'ECCBR',
    'EWCBR',
    'EWIMT',
    'EWHCI',
    'EWSN',
    'EWSA'
]
years = [
    '1995',
    '1996',
    '1997',
    '1998',
    '1999',
    '2000',
    '2001',
    '2002',
    '2003',
    '2004',
    '2005',
    '2006',
    '2008',
    '2009',
    '2010'
]

# measure the throughput (queries / sec)
def _through_query(conn, query:str, args:list) -> float:
    start = time.perf_counter()
    end = start
    run_count = 0
    measured_time = 0.0 # in ms
    with conn.cursor() as c:
        while (end - start < RUNTIME):
            print(query, '| progress:', int(end - start), '/', RUNTIME, 'sec', end='\r')
            measured_time += _analyze(c, query.replace('<arg>', args[run_count % len(args)])) # make sure we don't run out of bounds
            run_count += 1
            end = time.perf_counter()
        print(80*' ', '\r', end='')
    return round(run_count / (measured_time / 1000), 3)

def _reset(conn):
    print('resetting tables', end='\r')
    db.reset_tables(conn)
    db.fill_tables(conn)
    print(80*' ', '\r', end='')

def _idx(conn, attr:str, method:str, cluster:bool = False):
    print('indexing tables', end='\r')
    with conn.cursor() as c:
        c.execute('CREATE INDEX test_idx_' + attr + ' ON publ USING ' + method + ' (' + attr + ')')
        if cluster:
            c.execute('CLUSTER publ USING test_idx_' + attr)
        c.execute('ANALYZE publ')
    conn.commit() # just to be sure
    print(80*' ', '\r', end='')

def _explain(conn, query:str, args:list) -> str:
    with conn.cursor() as c:
        c.execute('EXPLAIN ' + query.replace('<arg>', args[0]))
        return '\n'.join(map(lambda el: el[0],c.fetchall()))

def _analyze(cursor, query:str) -> float:
    cursor.execute('EXPLAIN ANALYZE ' + query)
    return float(re.fullmatch(r"^Execution time: (?P<time>\d*\.\d*) ms$", cursor.fetchall()[-1][0]).groupdict()['time'])

if __name__ == '__main__':
    data_setup.run()
    conn = db.connect()

    point = "SELECT * FROM publ WHERE pubID = '<arg>'"
    multipoint_low = "SELECT * FROM publ WHERE booktitle = '<arg>'"
    multipoint_high = "SELECT * FROM publ WHERE year = '<arg>'"

    print('\n### point query ###\n')
    _reset(conn)
    print('  = sequential scan')
    print(_explain(conn, point, pubIDs))
    print('  > through', _through_query(conn, point, pubIDs), 'queries/s\n')

    _reset(conn)
    print('  = clustered B+')
    _idx(conn, 'pubID', 'btree', cluster= True)
    print(_explain(conn, point, pubIDs))
    print('  > through', _through_query(conn, point, pubIDs), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered B+')
    _idx(conn, 'booktitle', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'pubID', 'btree')
    print(_explain(conn, point, pubIDs))
    print('  > through', _through_query(conn, point, pubIDs), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered hash')
    _idx(conn, 'booktitle', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'pubID', 'hash')
    print(_explain(conn, point, pubIDs))
    print('  > through', _through_query(conn, point, pubIDs), 'queries/s\n')

    #############################################################################

    print('\n### multipoint low ###\n')
    _reset(conn)
    print('  = sequential scan')
    print(_explain(conn, multipoint_low, booktitles))
    print('  > through', _through_query(conn, multipoint_low, booktitles), 'queries/s\n')

    _reset(conn)
    print('  = clustered B+')
    _idx(conn, 'booktitle', 'btree', cluster= True)
    print(_explain(conn, multipoint_low, booktitles))
    print('  > through', _through_query(conn, multipoint_low, booktitles), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered B+')
    _idx(conn, 'title', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'booktitle', 'btree')
    print(_explain(conn, multipoint_low, booktitles))
    print('  > through', _through_query(conn, multipoint_low, booktitles), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered hash')
    _idx(conn, 'title', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'booktitle', 'hash')
    print(_explain(conn, multipoint_low, booktitles))
    print('  > through', _through_query(conn, multipoint_low, booktitles), 'queries/s\n')

    #############################################################################

    print('\n### multipoint high ###\n')
    _reset(conn)
    print('  = sequential scan')
    print(_explain(conn, multipoint_high, years))
    print('  > through', _through_query(conn, multipoint_high, years), 'queries/s\n')

    _reset(conn)
    print('  = clustered B+')
    _idx(conn, 'year', 'btree', cluster= True)
    print(_explain(conn, multipoint_high, years))
    print('  > through', _through_query(conn, multipoint_high, years), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered B+')
    _idx(conn, 'booktitle', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'year', 'btree')
    print(_explain(conn, multipoint_high, years))
    print('  > through', _through_query(conn, multipoint_high, years), 'queries/s\n')

    _reset(conn)
    print('  = non-clustered hash')
    _idx(conn, 'booktitle', 'btree', cluster= True) # cluster on other attribute
    _idx(conn, 'year', 'hash')
    print(_explain(conn, multipoint_high, years))
    print('  > through', _through_query(conn, multipoint_high, years), 'queries/s\n')

    conn.close()
