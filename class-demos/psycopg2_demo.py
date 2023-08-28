import psycopg2

PASSWORD = input('Postgres password please: ')

connection = psycopg2.connect(dbname = 'example', password = PASSWORD)

cursor = connection.cursor()

# reset table if it exists
cursor.execute('DROP TABLE IF EXISTS table2;')

cursor.execute('''
CREATE TABLE table2 (
    id INTEGER PRIMARY KEY,
    completed BOOLEAN NOT NULL DEFAULT False
    );
''')

# inserts
cursor.execute('INSERT INTO table2 (id, completed) VALUES (%s, %s);', (1, True))

SQL = 'INSERT INTO table2 (id, completed) VALUES (%(id)s, %(completed)s);'
data = {'id': 2, 'completed': False}
cursor.execute(SQL, data)

cursor.execute('INSERT INTO table2 (id, completed) VALUES (%s, %s);', (3, True))

# selections
cursor.execute('SELECT * FROM table2;')

result = cursor.fetchmany(2)
print('fetchmany(2)', result)

result2 = cursor.fetchone()
print('fetchone', result2)

cursor.execute('SELECT * FROM table2;')

result3 = cursor.fetchone()
print('fetchone', result3)

connection.commit()

connection.close()
cursor.close()