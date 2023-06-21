import psycopg


def connection():
    conn = psycopg.connect(
        user='tikhon',
        dbname='tennis_stat',
        host='localhost',
        password='123'
    )

    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM players LIMIT 1;
    ''')
    print(cur.fetchone())

    return conn

conn = connection()
cursor = conn.cursor()

