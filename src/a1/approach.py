

# APPROACH 0: Straigtforward
def straight(data_path: str, table: str, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        for line in file:
            data= line.split('\t')
            c.execute("INSERT INTO auth (name, pubID) VALUES (%s, %s)", (data[0].replace("'", ""), data[1]))
            conn.commit()

# APPROACH 1: Straigtforward + One transaction
def straight_onetrans(data_path: str, table: str, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        for line in file:
            data= line.split('\t')
            c.execute("INSERT INTO auth (name, pubID) VALUES (%s, %s)", (data[0].replace("'", ""), data[1]))
    conn.commit()

# APPROACH 1: Prepared Statements + One transaction
def prep_onetrans(data_path: str, table: str, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        c.execute('PREPARE authInsert1 (varchar (49) , varchar (129)) AS \
                INSERT INTO auth VALUES ($1 , $2)')
        for line in file:
            data= line.split('\t')
            c.execute('EXECUTE authInsert1 (%s, %s);', (data[0],data[1]))
    conn.commit()

# APPROACH 1: Prepared Statements + One transaction + Multi row insert
def prep_onetrans_multirow(data_path: str, table: str, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        c.execute('PREPARE authInsert2 (varchar (49) , varchar (129)) AS \
                INSERT INTO auth VALUES ($1 , $2),($3 , $4),($5 , $6),($7 , $8), \
                ($9 , $10),($11 , $12),($13 , $14),($15 , $16),($17 , $18),($19 , $20)')
        dataSet = []
        for line in file:
            dataSet.append(line.split('\t'))
            if len(dataSet) == 10:
                c.execute('EXECUTE authInsert2 ( \
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', \
                        (dataSet[0][0],dataSet[0][1],dataSet[1][0],dataSet[1][1], \
                        dataSet[2][0],dataSet[2][1],dataSet[3][0],dataSet[3][1], \
                        dataSet[4][0],dataSet[4][1],dataSet[5][0],dataSet[5][1], \
                        dataSet[6][0],dataSet[6][1],dataSet[7][0],dataSet[7][1], \
                        dataSet[8][0],dataSet[8][1],dataSet[9][0],dataSet[9][1]))
                dataSet = []
    conn.commit()

# APPROACH 2: ProstgreSQL Copy statement
def copy(data_path: str, table: str, conn):
    with open(data_path, 'r', encoding="utf-8") as file, conn.cursor() as c:
        c.copy_from(file, table)
    conn.commit()
