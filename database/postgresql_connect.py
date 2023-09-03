import psycopg
import os

from dotenv import load_dotenv

load_dotenv('.env')

owner = os.getenv("OWNER")
password = os.getenv("PASSWORD")
def connection():
    conn = psycopg.connect(
        user=owner,
        dbname='tennis_stat',
        host='localhost',
        password=password
    )

    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM players LIMIT 1;
    ''')
    print(cur.fetchone())

    return conn

conn = connection()
cursor = conn.cursor()

