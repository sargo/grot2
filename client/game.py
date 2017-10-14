"""
Play GROT2 game.
"""

import http.client
import json
import random


def get_move(data):
    """
    Get coordinates (start point) of next move.
    """
    return {
        'x': random.randint(0, 4),
        'y': random.randint(0, 4),
    }


def play(match_id, token, server, debug=False):
    """
    Connect to game server and play rounds in the loop until end of game.
    """
    # connect to the game server
    client = http.client.HTTPConnection(server)
    client.connect()
    match_url = '/match/{}?token={}'.format(match_id, token)

    # wait until the game starts
    client.request('GET', match_url)

    response = client.getresponse()
    headers = {'Content-type': 'application/json'}

    while response.status == 200:
        data = json.loads(response.read().decode())
        if data['moves'] == 0:
            if debug:
                print('Game Over!')
            break

        if debug:
            print('score: {}, moves: {}'.format(data['score'], data['moves']))

        # make your move and wait for a new round
        client.request('POST', match_url, json.dumps(get_move(data)), headers)

        response = client.getresponse()
