"""
Play GROT2 game.
"""

import random

import utils


def get_move(data):
    """
    Get coordinates (start point) of next move.
    """
    print(data['preview']['directions'], data['preview']['points'])
    rows_points = data['board']['points'].split('\n')
    rows_directions = data['board']['directions'].split('\n')
    for pair in zip(rows_directions, rows_points):
        print(*pair)
    print('')

    return {
        'row': random.randint(0, 4),
        'col': random.randint(0, 4),
    }


def play(match_id, token, server):
    """
    Connect to game server and play rounds in the loop until end of game.
    """
    match_url = '{}/match/{}'.format(server, match_id)
    # get initial state of a match
    response = utils.json_urlopen(match_url, headers={'x-api-key': token})

    while response['code'] == 200:
        data = response['json']
        if data['moves'] == 0:
            print('Game Over!')
            break

        # make your move and get data for the next round
        response = utils.json_urlopen(
            match_url,
            headers={'x-api-key': token},
            data=get_move(data),
            method='POST',
        )
