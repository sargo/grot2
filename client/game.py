"""
Play GROT2 game.
"""

from urllib.request import urlopen, Request
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


def play(match_id, token, server):
    """
    Connect to game server and play rounds in the loop until end of game.
    """
    match_url = 'https://{}/match/{}?token={}'.format(server, match_id, token)
    # get initial state of a match
    response = urlopen(match_url)

    while response.status == 200:
        data = json.loads(response.read().decode())
        if data['moves'] == 0:
            break

        # make your move and get data for the next round
        response = urlopen(Request(
            url=match_url,
            headers={'Content-type': 'application/json'},
            data=json.dumps(get_move(data)).encode(),
            method='POST',
        ))
