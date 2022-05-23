import psycopg2, os, codecs
from time import time
import approach, db, datagenerator

def test(f, conn):
    print('Testing approach:', f.__name__)

    db.reset_tables(conn)
    start = time()
    result = f(conn)
    end = time()

    print('>',round(end-start, 5),'sec')
    print(result, '\n')

if __name__ == '__main__':
    datagenerator.generate()
    conn = db.connect()

    test(approach.approach1_inefficient, conn)
    test(approach.approach1_efficient, conn)
    test(approach.approach1_inefficient_explained, conn)
    test(approach.approach1_efficient_explained, conn)

    test(approach.approach2_inefficient, conn)
    test(approach.approach2_efficient, conn)
    test(approach.approach2_inefficient_explained, conn)
    test(approach.approach2_efficient_explained, conn)

    conn.close()
