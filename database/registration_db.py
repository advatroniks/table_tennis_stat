from database.postgresql_connect import connection
from aiogram.dispatcher import FSMContext

conn = connection()


async def record_data(reg_data, cur: conn.cursor):
    cur.execute('''
               INSERT INTO players (name, surname, birthday, city,  game_style, telegram_id)
               VALUES
               (%s, %s, %s, %s, %s, %s)
           ''', (reg_data['name'],
                 reg_data['surname'],
                 reg_data['birthday'],
                 reg_data['city'],
                 reg_data['game_style'],
                 reg_data['telegram_id']
                 )

                )
    conn.commit()


async def check_registration_user(telegram_id, cur: conn.cursor) -> bool:
    cur.execute(f'''
        SELECT player_pid 
        FROM players
        WHERE telegram_id = {telegram_id}
    ''')

    if cur.fetchone() is None:
        print('t')
        return True
    elif cur.fetchone() is tuple:
        print('f')
        return False
