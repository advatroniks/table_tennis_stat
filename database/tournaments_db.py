from aiogram import types
from bot.database.postgresql_connect import conn

async def get_telegram_id(rival_name: str):
    cursor = conn.cursor()
    name_surname_list = rival_name.split()
    print(name_surname_list)
    cursor.execute('''
        SELECT telegram_id FROM players
        WHERE name = %s AND surname = %s
    ''',(name_surname_list[0].lower(), name_surname_list[1].lower())
                   )
    total_rival = cursor.fetchone()

    if total_rival is None:
        result = 'Incorrect_data'
    else:
        result = total_rival[0]

    return result


async def create_tournament(member_counts: int):
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO all_tournaments 
        (all_tournament_members) 
        VALUES ({member_counts})
        RETURNING all_tournament_id
    ''')

    tournament_id = cursor.fetchone()
    cursor.close()
    conn.commit()
    print(tournament_id)
    return tournament_id[0]


async def confirm_participation(telegram_id: int, tournament_id: str):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name || ' ' || surname 
        FROM players
        WHERE telegram_id = %s
    ''',(telegram_id,))
    name_surname = cursor.fetchone()[0]
    print(name_surname, telegram_id, tournament_id)

    cursor.execute('''
        UPDATE all_tournaments 
        SET players_list = players_list || '{"%s": "%s"}'
        WHERE all_tournament_id = '%s';
    ''' % (telegram_id, name_surname, tournament_id)
                   )


    # print(cursor.fetchone())

    conn.commit()
    cursor.close()



