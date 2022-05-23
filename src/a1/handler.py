import psycopg2, approach
from time import time
import os
import codecs

def test(f, data_path: str, table: str, conn):
    print('Testing approach:', f.__name__) # get python funcs name
    reset_tables(conn)
    start = time()
    f(data_path, table, conn)
    end = time()
    print('Inserted', table_entries(conn, table), 'tuples')
    print('>',round(end-start, 3),'sec')

def make_temp_data(insert_data_path: str,temp_data_path: str, percent: int):
    line_count = 0
    with open(insert_data_path, 'r', encoding='utf-8') as file:
        for line in file:
            dat = line.split('\t')
            line_count = line_count + 1
    if os.path.exists(temp_data_path):
        os.remove(temp_data_path)

    i = 0
    max_row = line_count / 100 * percent
    to_file = codecs.open(temp_data_path, 'a', 'utf-8')

    with open(insert_data_path, 'r', encoding='utf-8') as file:
        for line in file:
            to_file.write(line)
            i = i + 1
            if i >= max_row:
                break

def reset_tables(conn):
    with conn.cursor() as c:
        c.execute('DROP TABLE IF EXISTS auth')
        c.execute('DROP TABLE IF EXISTS publ')
        c.execute('''CREATE TABLE auth (
            name   VARCHAR(49),
            pubID  VARCHAR(256)
            )''')
        c.execute('''CREATE TABLE publ (
            pubID     VARCHAR(129),
            type      VARCHAR(13),
            title     VARCHAR(700),
            booktitle VARCHAR(132),
            year      VARCHAR(4),
            publisher VARCHAR(196)
            )''')
        conn.commit()

def table_entries(conn, table: str) -> int:
    with conn.cursor() as c:
        c.execute('SELECT COUNT(*) AS count FROM ' + table)
        res = c.fetchone()
        if res is None:
            raise Exception('empry response for count')
        else:
            return res[0]

if __name__ == '__main__':
    INSERT_DATA = 'data/auth.tsv'
    TEMP_DATA = 'data/temp.tsv'
    TEMP_PERCENT = 100

    # > database connect
    # connection = psycopg2.connect(dbname="dbtuning_ss2019", user="<name>", password="<pass>", host="biber.cosy.sbg.ac.at")
    connection = psycopg2.connect(dbname="postgres", user="postgres", password="admin") # local testing
    make_temp_data(insert_data_path= INSERT_DATA,temp_data_path= TEMP_DATA, percent= TEMP_PERCENT)

    print('Using ' + str(TEMP_PERCENT) + '% of data')
    #test(approach.straight, data_path= TEMP_DATA, table='auth', conn= connection)
    test(approach.straight_onetrans, data_path= INSERT_DATA, table='auth', conn= connection)
    test(approach.prep_onetrans, data_path= INSERT_DATA, table='auth', conn= connection)
    test(approach.prep_onetrans_multirow, data_path= INSERT_DATA, table='auth', conn= connection)
    test(approach.copy, data_path= INSERT_DATA, table='auth', conn= connection)

    connection.close()
