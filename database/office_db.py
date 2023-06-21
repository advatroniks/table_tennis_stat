from aiogram import types
from bot.database.postgresql_connect import conn



async def get_last_10_games(callback: types.CallbackQuery) -> list:
    telegram_id = callback.from_user.id
    cur = conn.cursor()

    cur.execute(f'''
        SELECT p1.name || ' ' || p1.surname, g.score_1, g.score_2, p2.name || ' ' || p2.surname, g.game_data
        FROM players AS p1 INNER JOIN games as g ON p1.player_id = g.player_1 
        INNER JOIN players AS p2 ON g.player_2 = p2.player_id 
        WHERE p1.telegram_id = {telegram_id} OR p2.telegram_id = {telegram_id}
        ORDER BY g.game_data DESC; 
    ''')

    data = cur.fetchall()
    return data


async def   get_win_loses_statistics(callback: types.CallbackQuery, query_param = 'telegram_id') -> tuple:
    telegram_id = callback.from_user.id
    cur = conn.cursor()

    cur.execute(f'''
        SELECT count(*) FROM games INNER JOIN players
        ON player_id = winner
        WHERE {query_param} = {telegram_id}
    ''')
    win_counts = cur.fetchone()[0]

    cur.execute(f'''
        SELECT count(*) FROM games AS g INNER JOIN players AS p1
        ON g.player_1 = p1.player_id INNER JOIN players AS p2
        ON p2.player_id = g.player_2
        WHERE p1.{query_param} = {telegram_id} OR p2.{query_param} = {telegram_id}
    ''')
    total_games = cur.fetchone()[0]

    total_result = (str(total_games), str(win_counts), str(total_games - win_counts))
    print(total_result)

    return total_result


async def get_lose_win_rate_player(player_id) -> tuple:
    cur = conn.cursor()
    cur.execute(f'''
        SELECT count(*) FROM games 
        WHERE player_1 = '{player_id}' OR player_2 = '{player_id}'
    ''')

    total_games = cur.fetchone()[0]

    cur.execute(f'''
        SELECT count(*) FROM games
        WHERE winner = '{player_id}'
    ''')

    win_games = cur.fetchone()[0]

    return (total_games, win_games, total_games - win_games)


async def get_personal_games(self_player_id, player_id) -> tuple:
    cur = conn.cursor()
    cur.execute(f'''
        SELECT p1.name || ' ' || p1.surname, g.score_1, g.score_2, p2.name || ' ' || p2.surname, g.game_data
        FROM players AS p1 INNER JOIN games as g ON p1.player_id = g.player_1
        INNER JOIN players AS p2 ON g.player_2 = p2.player_id
        WHERE (p1.player_id = '{player_id}' AND p2.player_id = '{self_player_id}') 
        OR (p1.player_id = '{self_player_id}' AND p2.player_id = '{player_id}') 
        ORDER BY g.game_data DESC LIMIT 5;  
    ''')

    return cur.fetchall()


async def get_personal_counter_win_lose(player_1, player_2) -> tuple:
    cur = conn.cursor()
    cur.execute(f'''
        SELECT count(*)
        FROM players AS p1 INNER JOIN games as g ON p1.player_id = g.player_1
        INNER JOIN players AS p2 ON g.player_2 = p2.player_id
        WHERE (p1.player_id = '{player_1}' AND p2.player_id = '{player_2}') 
        OR (p1.player_id = '{player_2}' AND p2.player_id = '{player_1}') 
    ''')
    total_games = cur.fetchone()[0]

    cur.execute(f'''
        WITH total_games AS 
        (
        SELECT *
        FROM players AS p1 INNER JOIN games as g ON p1.player_id = g.player_1
        INNER JOIN players AS p2 ON g.player_2 = p2.player_id
        WHERE (p1.player_id = '{player_1}' AND p2.player_id = '{player_2}') 
        OR (p1.player_id = '{player_2}' AND p2.player_id = '{player_1}')
        ) 
        SELECT count(*) FROM total_games WHERE winner = '{player_1}'
    ''')
    win_games = cur.fetchone()[0]
    lose_games = total_games - win_games
    return (total_games, win_games, lose_games)