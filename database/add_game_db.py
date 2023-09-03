import asyncio
from uuid import uuid4

import psycopg
from database.postgresql_connect import cursor, conn
from aiogram import types


async def get_rivals(rival_name: str):
    name_surname_list = rival_name.split()
    print(name_surname_list)
    cursor.execute('''
        SELECT player_id FROM players
        WHERE name = %s AND surname = %s
    ''',(name_surname_list[0].lower(), name_surname_list[1].lower())
                   )
    total_rival = cursor.fetchone()

    if total_rival is None:
        result = 'Incorrect_data'
    else:
        result = total_rival[0]

    return result


async def get_first_player(id_player_telegram):
    cursor.execute('''
        SELECT player_id FROM players 
        WHERE telegram_id = %s;
    ''' % id_player_telegram)

    player_id = cursor.fetchone()
    print(player_id[0])
    return player_id[0]


async def insert_data_score(game_data) -> None:
    if int(game_data['score_1']) > int(game_data['score_2']):
        winner = game_data['player_1']
    else:
        winner = game_data['player_2']

    cursor.execute('''
        INSERT INTO games (player_1, player_2, score_1, score_2, winner)
        VALUES
        (%s, %s, %s, %s, %s)
    ''', (game_data['player_1'], game_data['player_2'], game_data['score_1'], game_data['score_2'], winner)
                   )
    conn.commit()


async def insert_full_data_score(game_data, sets_count:int) -> None:
    if int(game_data['score_1']) > int(game_data['score_2']):
        winner = game_data['player_1']
    else:
        winner = game_data['player_2']

    cursor.execute('''
           INSERT INTO games (player_1, player_2, score_1, score_2, winner)
           VALUES
           (%s, %s, %s, %s, %s)
           RETURNING game_id
       ''', (game_data['player_1'], game_data['player_2'], game_data['score_1'], game_data['score_2'], winner)
                   )

    game_id = cursor.fetchone()[0]
    print(game_id)

    print(game_data.items())
    for i in range(1, sets_count + 1):
        first_player_set_name = f's1_{i}'
        second_player_set_name = f's2_{i}'
        first_player_value = game_data[f's1_{i}']
        second_player_value = game_data[f's2_{i}']
        cursor.execute(f'''
            UPDATE games
            SET {first_player_set_name} = {first_player_value}, {second_player_set_name} = {second_player_value}
            WHERE game_id = '{game_id}';
        ''')

    conn.commit()


