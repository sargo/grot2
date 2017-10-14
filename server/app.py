import random


from chalice import Chalice
from chalice import NotFoundError, BadRequestError

from grotlogic.board import Board
from grotlogic.match import Match
from grotlogic.player import Player

import settings
import db


app = Chalice(app_name='grot2-server')
app.debug = True


@app.route('/')
def index():
    return 'GROT2 server'


@app.route('/match', methods=['PUT'])
def match_put():
    user_id = 'ogras'
    match_id = db.new_match(user_id)
    return {'match_id': match_id}


@app.route('/match/{match_id}', methods=['GET'])
def match_get(match_id):
    user_id = 'ogras'
    return db.get_match(user_id, match_id).get_state()


@app.route('/match/{match_id}', methods=['POST'])
def match_post(match_id):
    user_id = 'ogras'
    match = db.get_match(user_id, match_id)
    if not match.is_active():
        raise BadRequestError('Game Over!')

    request = app.current_request
    data = request.json_body
    try:
        x = int(data['x'])
        y = int(data['y'])
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise BadRequestError('x or y is missing or not int')

    if not 0 <= x < settings.BOARD_SIZE or not 0 <= y < settings.BOARD_SIZE:
        raise BadRequestError('x or y is out of range')

    match.start_move(x, y)
    db.update_match(user_id, match_id, match)
    return match.get_state()


@app.route('/match/{match_id}/results', methods=['GET'])
def match_results_get(match_id):
    matches = db.get_all_matches(match_id)
    matches.sort(key=lambda i: int(i['score']), reverse=True)
    return {
        'players': [
            {'login': match['user_id'], 'score': match['score']}
            for match in matches
        ]
    }