

def approach1_inefficient(conn):
    with conn.cursor() as c:
        c.execute("SELECT ssnum FROM employee WHERE dept IN (SELECT dept FROM techdept)")
        rows = c.fetchall()
    return len(rows)

def approach1_efficient(conn):
    with conn.cursor() as c:
        c.execute("SELECT ssnum FROM employee, techdept WHERE employee.dept = techdept.dept")
        rows = c.fetchall()
    return len(rows)

def approach1_inefficient_explained(conn):
    with conn.cursor() as c:
        c.execute("EXPLAIN ANALYZE SELECT ssnum FROM employee WHERE dept IN (SELECT dept FROM techdept)")
        rows = c.fetchall()
    return rows

def approach1_efficient_explained(conn):
    with conn.cursor() as c:
        c.execute("EXPLAIN ANALYZE SELECT ssnum FROM employee, techdept WHERE employee.dept = techdept.dept")
        rows = c.fetchall()
    return rows

def approach2_inefficient(conn):
    with conn.cursor() as c:
        c.execute("SELECT AVG(salary) as avgsalary, dept FROM employee GROUP BY dept HAVING dept = 'dept 1'")
        rows = c.fetchall()
    return rows[0][0]

def approach2_efficient(conn):
    with conn.cursor() as c:
        c.execute("SELECT AVG(salary) as avgsalary, dept FROM employee WHERE dept = 'dept 1' GROUP BY dept")
        rows = c.fetchall()
    return rows[0][0]

def approach2_inefficient_explained(conn):
    with conn.cursor() as c:
        c.execute("EXPLAIN ANALYZE SELECT AVG(salary) as avgsalary, dept FROM Employee GROUP BY dept HAVING dept = 'dept 1'")
        rows = c.fetchall()
    return rows

def approach2_efficient_explained(conn):
    with conn.cursor() as c:
        c.execute("EXPLAIN ANALYZE SELECT AVG(salary) as avgsalary, dept FROM Employee WHERE dept = 'dept 1' GROUP BY dept")
        rows = c.fetchall()
    return rows
