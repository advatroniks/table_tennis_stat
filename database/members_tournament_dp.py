from database.postgresql_connect import conn
from database.add_game_db import get_first_player
from database.tournaments_db import add_game_rating_in_tournament


async def add_game_to_database(
        first_player: str,
        second_player: str,
        score: str,
        tournament_id: str,
        tournament_key=None
) -> None:
    cursor = conn.cursor()

    first_player_id = await get_first_player(first_player)
    second_player_id = await get_first_player(second_player)

    if int(score[0]) > int(score[-1]):
        winner = first_player_id
        await add_game_rating_in_tournament(telegram_id=first_player,
                                            tournament_id=tournament_id,
                                            point=2)
        await add_game_rating_in_tournament(telegram_id=second_player,
                                            tournament_id=tournament_id,
                                            point=1)

    else:
        winner = second_player_id
        await add_game_rating_in_tournament(telegram_id=second_player,
                                            tournament_id=tournament_id,
                                            point=2)
        await add_game_rating_in_tournament(telegram_id=first_player,
                                            tournament_id=tournament_id,
                                            point=1)

    cursor.execute("""
        INSERT INTO games (player_1, player_2, score_1, score_2, winner, all_tournament_id)
        VALUES ('%s', '%s', %s, %s, '%s', '%s')  
    """ % (first_player_id, second_player_id, int(score[0]), int(score[-1]), winner, tournament_id)
                   )

    conn.commit()
    cursor.close()



