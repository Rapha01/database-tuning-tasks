# database-tuning-tasks
Explore different approaches to database tuning using multiple techniques for more efficient queries and database behavior. Focuses on bulk data writing, query tuning, index tuning, join tuning and concurrency tuning.

## A1: Bulk data writing

### Implementation
At first, the table Auth is created if it doesn’t exist already. The
auth.tsv file is read line by line with Python. For each line, a new INSERT2 query
is performed through the adaptor3. Also, for each inserted tuple, a COMMIT4 is issued,
resulting in excessive runtime.

### Efficient Approach 1: Reduce Overhead
#### Saving transactions
Instead of opening and closing a transaction for every insert,
we commit only after every insert statement has been issued. For this we need to place
the commit after, and not in, our insert loop.

#### Prepared statements.
We create an SQL template statement, so the preparation
(parsing and optimizing) for the query can be done once in foresight and will be saved
for future use. For this we need to define the template using the PREPARE command.
Similar to the definition of a function, we need to define parameter(types), semantics
(the actual query) and give it a name to call it later.

#### Multirow insert.
Instead of inserting one entry per query, we use the INSERT com-
mands functionality to insert multiple rows per query.

#### Why is this approach efficient?
#### One transaction
PostgreSQL has significant per-transaction overhead, including log
output and visibility rules which need to be set with each transaction.5 If you allow each
insertion to be committed separately, PostgreSQL is doing a lot of work for each row
that is added6. Hence bundling queries into transactions will reduce execution time.

#### Prepared statements
When the PREPARE statement is executed, the specified
statement is parsed, analyzed, and rewritten. When an EXECUTE command is subse-
quently issued, the prepared statement is planned and executed. This division of labor
avoids repetitive parse analysis work, while allowing the execution plan to depend on the
specific parameter values supplied. Prepared statements have the largest performance
advantage when a single session is being used to execute a large number of similar
statements.6 (in our case a large number of similar inserts).

#### Multirow insert
Multi-row insert needs the statement to be parsed, prepared and
changes written to WAL only once, therefore resulting in less overhead.

#### Tuning principle
Start-Up costs are high & running costs are low.
The initial overhead (start-up cost) for each transaction or query is significant, while
the actual operation on the database (running cost) is small. Hence it makes sense to
do more running per start-up - do multiple queries per transaction and multiple inserts
per query.

### Efficient Approach 2: SQL COPY
#### Implementation
PostgreSQL provides an efficient way of moving data from a file to
a table. “COPY with a file name instructs the PostgreSQL server to directly read from
or write to a file.”8 We used the COPY FROM statement as it copies from a file to the
database. It is assumed that each tuple is in a separate line in the file, and the delimiter
between columns can be set if necessary (default is tab anyway). The PostgreSQL server
will append data from the file to the specified table. Our database adaptor also supports
this statement

#### Why is this approach efficient?
Each SQL query needs to be parsed and optimised
before it is executed. For our improved solution (with PREPARE) some overhead for the
straightforward approach is removed. However, the parser still has to process each call
to the prepared statement and we need to supply the tuple fields via python (which is
rather slow). “The COPY command is optimised for loading large numbers of rows”10.
It is only one single query, which will read the data directly from the file to the table.
So simplified, the database system may just copy the tuples from a sequential read of
the file to a sequential write to the table. There is some overhead for determining the
delimiter between columns, but this is of course in total still faster than our improved
PREPARED approach.

#### Tuning principle
Start-Up costs are high & running costs are low.
In essence, the write process is started once and then all the data inside the file is
sequentially appended to the table. There is no real interrupt to the operation (despite
of course low-level ones, such as the head of a hard disk, moving to a new block).

#### Results
Approach Runtime [sec]
Straightforward 3533 ( 1h)
Straightforward (single transaction) 870 ( 15min)
Prepared Statements 798 ( 13min)
Prepared Statements (multi-row) 144 ( 2min)
Copy 8

## A2: Query tuning

### Populating the Tables
We wrote a python script which creates three tsv files (Employee.tsv, Student.tsv and
Techdept.tsv). All values are random, except the key values which are unique. The
ssnum from the Employee.tsv starts with 1 and goes to 70.000. The other 30.000 (70.000-
100.000) are shared between Employee and Student. Of course this 30.000 have the same
name. The Techdept.tsv contains 10 depts (”dept 1”,..., ”dept 10”). Every Employee
gets an random dept, this way we will reach the 10 percent hopefully. After creating the
files, we use the COPY method for performance reasons.
ssnum starts with 1 and increase with every new Employee or Student. name starts with
AAAAAA, AAAAAB, AAAAAC and so on.

### Query 1
#### Evaluation of the Execution Plans
In postgresql, a MERGE JOIN “requires that the input data is sorted on the join keys”.
Postgresql may even walk through the index to retrieve the rows in correct order1.
All indices in postgresql are stored as secondary indices, meaning they are separated
from the actual data in the database. In case an index is only used to read the actual
index attribute itself, only the index is accessed and not the corresponding table. This
is called “Index Only Scan”2.
For this query, the query optimizer uses a MERGE JOIN since there exists an index on
both join attributes and they are not sorted by this attribute (otherwise a sequen-
tial scan would be faster). For the attribute student.name, an “Index Only Scan”
is enough cause no other attribute of student is used. However, since the attribute
employee.ssnum is selected, an “Index Only Scan” cannot be performed for the join
attribute employee.name.

#### Rewritten Query
Again, the query optimizer uses a MERGE JOIN since there exists an index on both
join attributes and they are not sorted by this attribute (otherwise a sequential scan
would be faster). Since now, only the direct index attributes are needed (student.name,
employee.name), an “Index Only Scan” can be used for both indices.

#### Differences
In the original query, an “Index Scan” of the index on employee.name
is used to access the tuples of employee, while in the rewritten query an “Index Only
Scan” of the index on employee.ssnum is used.
Runtime [ms]
Original query 250.4
Rewritten query 152.8

#### Experiment
The “Index Scan” of empl name idx in the original query is slower than
the “Index Only Scan” of empl ssnum idx, since the actual rows in the table need to be
accessed to retrieve also employee.ssnum.

### Query 2
#### Evaluation of the Execution Plans
Postgresql is using a MERGE JOIN since both join attributes are available as sorted indices.
For the index techdept.dept, even an “Index Only Scan” is possible since only the
indexed attribute is needed. The result is then sorted with quicksort and duplicates
are removed to fulfil the DISTINCT requirement.
This is actually not necessary since there are no duplicates in the result of the merge.
Employee is a privileged table and Techdept reaches it through it’s key techdep.dept.

#### Rewritten Query
The rewritten execution plan is similar to the original one, but doesn’t contain the
sorting and duplicate-removal since no DISTINCT was used in the query.

#### Discussion
There is no sorting and duplicate-removal as the DISTINCT is not used
in the rewritten query.
Runtime [ms]
Original query 31.6
Rewritten query 23.6

#### Experiment
There is no sorting and duplicate-removal as the DISTINCT is not used in
the rewritten query. This makes the rewritten query faster, of course.


## A3: Index Tuning

### Index Data Structures
Which index data structures (e.g., B+ tree index) are supported?
• B+-tree (data pointers only on leaf level)
• hashindex
• special for text searches:
– GiST (Generalized Search Tree)
“lossy because each document is represented in the index by a fixed-length
signature, [created by] hashing each word into a single bit in an n-bit string,
with all these bits OR-ed together to produce an n-bit document signature”
– GIN (Generalized Inverted Index)
“contain[s] an index entry for each word”, (“inverted” because it maps content
to data)
• SP-GiST (partitioned search trees)
“different non-balanced data structures, such as quad-trees, k-d trees, and radix
trees”
• BRIN (when columns are correlated with physical table order)

### Clustering Index
First, the desired index is created with the CREATE INDEX statement. Both hash and
B+-tree may be selected explicitly, though B+-tree is used by default.

Finally, the CLUSTER statement is used to physically sort the table according to the
clustered index. This is a one-time operation, hence, if new tuples are inserted into the
table or old ones change, the table is not updated. It is recommended to re-run this
command if an up-to-date index is desired.

The CLUSTER command may be invoked with any defined index for a table. The only
limitation is that only one clustered index can exist for a table at a time, since the table
can only be sorted according to one index at a time.

A table is not automatically reorganised when new tuples are inserted. The CLUSTER
command is simply used to physically order the data (once) and all new data goes to
the end of the table.2 However, a tables fill factor may be adjusted by changing it’s
fillfactor parameter. This can aid in preserving cluster ordering during updates,
since updated rows are kept on the same page if enough space is available.

The approach PostgreSQL has taken to cluster means that unlike the SQL Server ap-
proach, there is no additional penalty during transactions of having a clustered index.
In the SQL Server approach all non-clustered indexes are keyed by the clustered index,
which means any change to a clustered field requires rebuilding of the index records for
the other indexes and also any insert or update may require some amount of physical
shuffling.

### Non-Clustering Indices
By default indexes are not clustered. To create a clustered index it has to be specified
as such .1. For creating a composite index in postgresql it is only necessary to mention
all fields, instead of one.

PostgreSQL can perform index-only scans under the following conditions 4
(1.) The index type must support index-only scans. B-tree indexes always do. The
underlying requirement is that the index must physically store, or else be able to recon-
struct, the original data value for each index entry.
(2.) The query must reference only columns stored in the index.
If an index is covering relating to a specific query, condition (2.) is met. If the index
type also supports index-only scans (1.), the system can take advantage of it by using
an index-only scan.
A covering index is an index specifically designed to include the columns needed by a
particular type of query. 4 Columns in the condition of a query are needed.
Assume that the condition is not a prefix of the attribute sequence, but the index still
covers the query. This means the condition must not contain any attributes and can
only be something trivial like ’true’. Otherwise it is not covering anymore and can not
be taken advantage of via an index-only can (as not all needed information is accessible
in the index, and the actual table entries have to be retrieved from the heap).

After an index is created, the system has to keep it synchronized with the table. This
adds overhead to data manipulation operations. Therefore indexes that are seldom or
never used in queries should be removed.
Creating an index on a large table can take a long time. By default, PostgreSQL allows
reads (SELECT statements) to occur on the table in parallel with index creation, but
writes (INSERT, UPDATE, DELETE) are blocked until the index build is finished.5
In PostgreSQL B-tree indexes always support index-only scans. GiST and SP-GiST
indexes support index-only scans for some operator classes but not others. Other index
types have no support.

### Key Compression and Page Size
Key compression: Prefix compression is possible with normalized keys.6
Default disk page: 8.192 Byte, this value can only be changed in the sourcecode and
then you have to compile your own version of postgreSQL.7 Therefore, it is not possible
to store very large field values directly. To overcome this limitation, large field values are
compressed and/or broken up into multiple physical rows. This happens transparently
to the user, with only small impact on most of the backend code. The technique is
affectionately known as TOAST (or ”the best thing since sliced bread”). TOAST stands
for The Oversized-Attribute Storage Technique.


## A4: Index Tuning – Selection
### Clustering B+ Tree Index
#### Point Query
We randomly selected a list of 15 pubIDs from our test data.
Show the runtime results and compute the throughput.
As we let our program run for a minute, we calculated our thoughput: 28654.625 queries/s

#### Multipoint Query – Low Selectivity
2539.836 queries/s

#### Multipoint Query – High Selectivity
11.28 queries/s

### Non-Clustering B+ Tree Index
#### Point Query
28432.221

#### Multipoint Query – Low Selectivity
1299.965 queries/s

#### Multipoint Query – High Selectivity
3.725 queries/s

### Non-Clustering Hash Index
#### Point Query
44550.557 queries/s

#### Multipoint Query – Low Selectivity
977.823 queries/s

#### Multipoint Query – High Selectivity
3.532 queries/s

### Table Scan
#### Point Query
0.649 queries/s

#### Multipoint Query – Low Selectivity
0.643 queries/s

#### Multipoint Query – High Selectivity
0.727 queries/s

### Discussion
|                        | clustering B+ | non-clust. B+ | non-clust. hash | table scan |
|------------------------|---------------|---------------|-----------------|------------|
| point (pubID)          | 28654.625     | 28342.221     | 44550.557       | 0.649      |
| multipoint (booktitle) | 2539.836      | 1299.965      | 977.823         | 0.643      |
| multipoint (year)      | 11.28         | 3.725         | 3.532           | 0.727      |

#### Types of queries
For indexed queries in general, the throughput is high for pointqueries since only one
record needs to be retrieved. The throughput decreases, the weaker the selectivity
gets (point > multipoint low > multipoint high). This is expected, since more and
more records are accessed. The throughput for the table scan (no index) does not vary
significantly across all query types. With no index, all records have to scanned in any
case. As expected, the number of matching records does not change execution time
significantly. (It should be noted that the table scan throughput for the point query
does not vary here, since the database doesn’t know that pubID is a unique value (no
constraints were created). Hence, the whole table is scanned here as well as there might
be more than one tuple, matching the condition.)

#### Clustering vs non-clustering B+ index
There is almost no difference between clustering and non-clustering B+ tree indices when
using point queries. This is due to the fact that only one tuple is retrieved and hence,
the sorted property of the table is of no use.
With weaker selectivity of multipoint queries, more and more records need to be retrieved
and the clustering has more effect on the throughput, enabling more queries per second.
With clustering, fewer page loads and index accesses are required as the result records
can be read from consecutive pages.

#### Hash index
The hash index shows the highest throughput for point queries, as the bucket address
can be computed without disk access, while the B+ trees requires additional disk accesses
to traverse the tree.
For the strongly selective multipoint query, the hash index has lower throughput than
the B+ tree. This is due to that fact that in the tree structure, consecutive pointers to

results are stored in one leaf. On the other hand, the bucket of the hash index for a
value may also contain other pointers, in case there was a collision of the hash function
for this value. This leads to more time spent on collecting all pointers. The whole effect
is not present for the weak multipoint query. The attribute year as less distinct values
than booktitle, hence collisions of the hash function are less likely and the hash bucket
contains only pointers to the requested year.

#### Table scan
The table scan shows the worst, but also the most constant performance of all experi-
ments in any type of query. With weaker selectivity the indexed queries approach the
table scans throughput. Our weakest selectivity (a certain year) still returns only a quite
small portion of the data. If even more records are to be returned, the table scan will
eventually outperform an indexed query, as a scan is by factor 2-10 faster than accessing
many pages through any index.

## A5: Join Tuning
### Join Strategies Proposed by System
#### Response times
|                                         | vJoin Strategy Q1 (s) | Join Strategy Q2 (s) |
|-----------------------------------------|-----------------------|----------------------|
| no index                                | Join (137.74)         | Hash Join (3.18)     |
| unique non-clustering on Publ.pubID     | Hash Join (15.05)     | Nested Loop (1.22)   |
| clustering on Publ.pubID and Auth.pubID | Merge Join (9.12)     | Nested Loop (1.18)   |

#### Discussion
The first query has a higher runtime for all types of indexes. This is expected, as Q1 joins
all tuples of Auth, while Q2 already restricts the join tuples by Auth.name =’Divesh
Srivastav’.
We have the highest runtime when no index is used and performance increases as indexes
are added. This is expected because with an index, we do not have to scan the inner
relation to find matching tuples. Clustering further increases the performance as the
sorted property can be exploited.

#### No index
Without any index, the database system has two (reasonably fast) choices: merge join
or hash join. For the the merge join, table scans are required and both tables are then
sorted. The hash join requires the two tables to be hashed into buckets. Then, for each
bucket containing also tuples from Auth (outer relation), a hash index is built on the
tuples from Publ (inner relation) within that bucket. Finally the tuples from Auth are
hashed with that new hash function to find matching pairs. Auth (outer relation) is
already restricted to one author name in Q2. We suspect that in this case, only few
buckets with both tuples from Auth and Publ are created so only few new hash indices
need to be constructed. In case of Q1, the whole relation Auth would participate in a hash
join, resulting in a lot of such matching buckets. Hence, many new hash indices would
be build and the database system chooses the merge join for increased performance.

#### Non-clustering Publ.pubID
It is obvious to choose an indexed nested loop join in case an index is present on the
inner relation (Publ). For each tuple on the outer relation (Auth), the index is used to
find the matching pairs in the inner relation. This in many cases faster than a merge
or hash join. However, the database system chose to use a hash join anyway for Q1.
This is because an indexed nested loop join is only efficient if the outer relation has less
records than the inner one has pages. Since in Q1, the whole table Auth participates in
the join, this is not the case here and the hash join will be faster.

#### Clustering Publ.pubID and Auth.pubID
Because of the clustering, the merge sort can be applied without the need to reorder
first. This gives the highest performance as each block from both relations has to be
loaded only once. Because of the strong selectivity of Q2 a merge join takes even longer
than a nested loop, where not all blocks of the inner relation have to be loaded.

### Indexed Nested Loop Join
#### Response times
|                                    | Response time Q1 [s] | Response time Q2 [s] |
|------------------------------------|----------------------|----------------------|
| index on Publ.pubID                | 76.61                | 1.30                 |
| index on Auth.pubID                | 39.01                | 159.42               |
| index on Publ.pubID and Auth.pubID | 36.71                | 1.20                 |

#### Query 1
##### Index on Publ.pubID (Q1/Q2)
Even tough Auth is the bigger relation and thus causes more iterations and block loads
for our outer loop, the system uses it as outer relation. It does this expectedly because of
the possibility to use an index with our inner relation (which only exists on Publ.pubID).
The savings from not having to check every tupel of the inner relation for every tupel of
the outer relation far outweighs the cost of extra iterations for using the bigger as outer
relation.

##### Index on Auth.pubID
As expected the performance of an index on Auth.pubID is even better, because the
system can use the smaller relation Publ as outer relation, while the bigger relation is
indexed. Compared to the previous index on Publ.pubID, we have far less iterations for
our outer loop, while the increase of the lookup cost of the bigger inner relation is not
that significant, because of the index.

##### Index on Publ.pubID and Auth.pubID
Compared to the previous index on Auth.pubID, there is no significant perfomance boost
as the system can only use the nested loop one way or another and cannot exploit the
index on both tables simultaneously. As expected the system uses the faster way, where
the bigger relation is indexed and the smaller looped through.

#### Query 2
Index on Publ.pubID
Like for Q1, we have an index on the smaller relation Publ.pubID that can still be used
to decrease runtime. Due to the restriction Auth.name =’Divesh Srivastav’ it makes
even more sense to use Auth as outer relation. This is because the system does not need
to look at the inner relation for every tuple of the outer relation. This way a lot index
lookups on the inner relation can be saved, as the selection on Auth is very strong.

##### Index on Auth.pubID
The database has to restrict the relation Auth by Auth.name =’Divesh Srivastav’.
Since there is no index on Auth.name, there are only two options for the system. Use an
index nested loop join with Auth as inner relation (like for Q1) and restrict the result
to one name. Or to first apply the constraint to the table and then use it in a normal
nested loop join. The first choice is obviously not very performant as the join would
involve more tuples and the filter would need to search through more tuples afterwards.
Hence, the database chooses the later approach. This approach is still slower than Q1
despite the stronger selectivity, since Auth needs to be filtered first.

##### Index on Publ.pubID and Auth.pubID
Here we can also see a difference of choice of the system between Q1 and Q2 because
of the restriction on Auth.name we have for Q2. While for Q1 the system uses Publ as
outer relation because of its size, for Q2 we see that it uses Auth as outer relation. This
is because the restricted Auth relation has then less tuples than Publ.

### Sort-Merge Join
|                            | Response time Q1 [s] | Response time Q2 [s] |
|----------------------------|----------------------|----------------------|
| no index                   | 136.91               | 43.26                |
| two non-clustering indexes | 10.40                | 4.65                 |
| two clustering indexes     | 9.15                 | 4.19                 |

#### Discussion
With any type of indexes, Q2 has a similar performance boost compared to Q1. This
is expected, because the system can drastically reduce the amount of tuples inside the
relation, before doing the sorting and merging. For Q2, the system does not use the
index on Auth, instead it filters the relation for the restriction first, in order to have less
tuples to merge.

#### No Index
As expected the queries take the longest with no index, because both relations need to
be sorted before the merge. Again Q2 is faster since there are less tuples to join.

#### Two non-clustering indexes
When indexes (on the respective join attributes) are available, then the database can
traverse the index and follow the respective pointers to join the tuples. For arbitrary
sorted tables, this might be quite slow since for one tuple from Publ, potentially many
table pages of Auth need to be loaded to retrieve the join pairs. However, our Auth and
Publ tables are already filled in sorted order, since the two files are sorted with respect
to pubID. So in essence the two tables are here also read sequentially (though via the
index). Because of this, the clustered index-version is not really faster than the non-
clustered version in our case. Finally Q2 is faster again because of the stronger selectivity.

#### Two clustering indexes
The clustered version is (in our case) not significantly faster than the non-clustered
version. This is because even for the non-clustered case, the tables are actually physically
sorted, as stated above. Again, Q2 is faster because of the stronger selectivity.

### Hash Join
|          | Response time Q1 [ms] | Response time [ms] Q2 |
|----------|-----------------------|-----------------------|
| no index | 18.18                 | 3.23                  |

#### Discussion
As we can see the Hash Join is a good way to join two relations without index. The
Hash Join is always faster then the other Join strategies without indexes.
With indexes the Sort-Merge Join performs better than than the Indexed Nested Loop
Join. Except if we have a strong selectivity like Q2 does (though, only when we have
indexes on Publ).
In general its always good to have indexes on all relations. At least an index on the most
important attributes if memory is rare. There is always a trade off between efficiency and
storage. Clustered Indexes are in every case a much better choice than the non-clustered
ones.

## A6: Concurrency Tuning
### Solution (a)
#### Read Committed
| Concurrent Transactions | Throughput | [transactions/sec] Correctness |
|-------------------------|------------|--------------------------------|
| 1                       | 73.624     | 100%                           |
| 2                       | 106.714    | 75%                            |
| 3                       | 121.313    | 76%                            |
| 4                       | 132.169    | 78%                            |
| 5                       | 143.822    | 73%                            |

#### Serializable
| Concurrent Transactions | Throughput | [transactions/sec] Correctness |
|-------------------------|------------|--------------------------------|
| 1                       | 68.687     | 100%                           |
| 2                       | 103.977    | 100%                           |
| 3                       | 114.763    | 100%                           |
| 4                       | 122.361    | 100%                           |
| 5                       | 130.342    | 100%                           |

### Solution (b)
#### Read Committed
#Concurrent Transactions Throughput [transactions/sec] Correctness
| Concurrent Transactions | Throughput | [transactions/sec] Correctness |
|-------------------------|------------|--------------------------------|
| 1                       | 78.056     | 100%                           |
| 2                       | 112.247    | 100%                           |
| 3                       | 125.310    | 100%                           |
| 4                       | 139.956    | 100%                           |
| 5                       | 148.449    | 100%                           |

#### Serializable
#Concurrent Transactions Throughput [transactions/sec] Correctness
| Concurrent Transactions | Throughput | [transactions/sec] Correctness |
|-------------------------|------------|--------------------------------|
| 1                       | 74.740     | 100%                           |
| 2                       | 108.977    | 100%                           |
| 3                       | 126.346    | 100%                           |
| 4                       | 131.394    | 100%                           |
| 5                       | 136.893    | 100%                           |

### Discussion
#### Solution (a & b) Throughput
The throughput for all queries and isolation levels rises
with the number or threads working on it.
For both transactions, the throughput is better when using the Read Committed isola-
tion level. This is faster, because it releases read locks after the read and, in case of an
update conflict, will wait for the updating transaction to commit, but not roll back. The
Serializable isolation level has strict locking, which results is longer locks, more overhead
and, in case of an update conflict, will roll back.

#### Solution (a) Correctness
In Postgresql, non-repeatable and phantom reads are pos-
sible at the transaction level when using the Read Commited isolation level. When we
retrieve and store our value in two separate steps a race condition may occur. If two
transactions read the current value of the companies bank account before updating it,
one of the decrement operations will get lost, as they are applied to the same value.

This can be represented in the following example:
Thread 1:
c = SELECT balance FROM Accounts WHERE account =0
Hence, cT 1 is some x. And the read lock on the company tuple is released.

Thread 2:
c = SELECT balance FROM Accounts WHERE account =0
Hence, cT 2 is the same x as for cT 1. And the read lock on the company tuple is released.

Thread 1:
UPDATE Accounts SET balance = c-1 WHERE account =0
Hence, the company balance is cT 1 − 1 = x − 1 and the write lock on the company tuple
is released since the transaction ends.

Thread 2:
UPDATE Accounts SET balance = c-1 WHERE account =0
Hence, the company balance is cT 2 − 1 = x − 1 and the write lock on the company tuple
is released since the transaction ends.

So in the end, the company balance was only decremented once but should’ve been
decremented twice. This whole effect increases, the more threads are used. Hence the
correctness gets worse for more threads.
None of these undesired phenomenas can happen with the Serializable isolation level.
Due to the strict two-phase locking it is always correct.

#### Solution (b) Correctness
In Postgresql non-repeatable and phantom reads are not
possible within a single SQL statement when using the Read Commited isolation level.
Even when using this isolation level our specific transaction does not allow for unwanted
concurrent phenomenas, as it contains only a single SQL statement. Hence the race
condition from Transaction A cannot occur here.
