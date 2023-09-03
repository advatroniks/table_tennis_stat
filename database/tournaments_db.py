from aiogram import types
from bot.database.postgresql_connect import conn


async def get_telegram_id(rival_name: str):
    cursor = conn.cursor()
    name_surname_list = rival_name.split()
    print(name_surname_list)
    cursor.execute('''
        SELECT telegram_id FROM players
        WHERE name = %s AND surname = %s
    ''', (name_surname_list[0].lower(), name_surname_list[1].lower())
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


async def confirm_participation(telegram_id: int, tournament_id: str) -> str:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name || ' ' || surname 
        FROM players
        WHERE telegram_id = %s
    ''', (telegram_id,))
    name_surname = cursor.fetchone()[0]
    print(name_surname, telegram_id, tournament_id)

    cursor.execute('''
        UPDATE all_tournaments 
        SET players_list = players_list || '{"%s": "%s"}'
        WHERE all_tournament_id = '%s';
    ''' % (telegram_id, name_surname, tournament_id)
                   )

    conn.commit()
    cursor.close()

    return name_surname


async def get_name_surname_capitalize_on_telegram_id(telegram_id: int | str) -> str:
    cursor = conn.cursor()
    cursor.execute('''
            SELECT name || ' ' || surname 
            FROM players
            WHERE telegram_id = %s
        ''', (telegram_id,))
    name_surname = cursor.fetchone()[0]
    template_list_to_transformation = name_surname.split()

    total_string_capitalize = ''.join([word.capitalize() for word in template_list_to_transformation])

    return total_string_capitalize


async def set_active_tournament(tournament_id: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE all_tournaments
        SET all_tournament_is_active = 1
        WHERE all_tournament_id = '%s'
    ''' % (tournament_id))
    conn.commit()
    cursor.close()


async def insert_members_message_id(telegram_id: int, message_id: int, member_name: str) -> None:
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE all_tournaments
        SET players_list = jsonb_set(players_list, '{%s}', '["%s", "%s", "0"]')
        WHERE all_tournament_is_active = 1 AND players_list ? '%s'
    ''' % (telegram_id, member_name, message_id, telegram_id)
                   )
    conn.commit()
    cursor.close()


async def add_game_rating_in_tournament(telegram_id: str | int, tournament_id: str, point: int) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
            WITH digit AS 
            ( 
            SELECT (players_list #>> '{%s, 2}')::int + %s 
            FROM all_tournaments 
            WHERE all_tournament_id = '%s'
            )
            UPDATE all_tournaments 
            SET players_list = jsonb_set
            (
            players_list, '{%s, 2}', to_jsonb((SELECT * FROM digit)::text) 
            ) 
            WHERE all_tournament_id = '%s';
        """ % (telegram_id, point, tournament_id, telegram_id, tournament_id)
    )

    conn.commit()
    cursor.close()


async def get_telegram_id_message_id(tournament_id: str):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT players_list
        FROM all_tournaments
        WHERE all_tournament_id = '%s'
    ''' % (tournament_id,))

    return cursor.fetchone()[0]


async def get_message_id_in_active_tournament(telegram_id: str) -> int:
    cursor = conn.cursor()
    cursor.execute('''
        SELECT players_list #>> '{%s, 1}' 
        FROM all_tournaments
        WHERE all_tournament_is_active = 1 AND players_list ? '%s';
    ''' % (telegram_id, telegram_id)
                   )

    return int(cursor.fetchone()[0])


async def check_player_confirmed_tournament(telegram_id: str, tournament_id: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT players_list ? '%s'  
        FROM all_tournaments
        WHERE all_tournament_id = '%s'
        """ % (telegram_id, tournament_id)
    )

    result = cursor.fetchone()[0]
    cursor.close()

    return result


# def add_live_games(games: list, tournament_id: str) -> None:
#     cursor = conn.cursor()
#     cursor.execute('''
#         UPDATE all_tournaments
#         SET live_games = ARRAY%s
#         WHERE all_tournament_id = '%s';
#     ''' % (games, tournament_id)
#                    )
#     conn.commit()
#     cursor.close()


async def get_name_surname_on_telegram_id(telegram_id: str) -> str:
    telegram_id = int(telegram_id)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, surname 
        FROM players
        WHERE telegram_id = %s
    """ % (telegram_id,)
                   )
    total_string = ''
    for i in cursor.fetchone():
        total_string += f' {i}'
    cursor.close()

    return total_string


async def get_all_members_rating(tournament_id: str) -> dict:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT players_list 
        FROM all_tournaments
        WHERE all_tournament_id = '%s'
    """ % (tournament_id,)
                   )
    result = cursor.fetchone()[0]
    cursor.close()

    return result
