import os
import random

from chalice import Chalice, CORSConfig, NotFoundError, BadRequestError

from chalicelib import apigateway
from chalicelib import gh_oauth
from chalicelib import s3
from chalicelib import sdb
from chalicelib import settings
from chalicelib import utils


app = Chalice(app_name=settings.APP_NAME)
app.debug = settings.DEBUG

cors_config = CORSConfig(
    allow_origin=os.environ.get('CORS_ALLOW_ORGIN', settings.CORS_ALLOW_ORGIN),
    max_age=86400,
)


@app.route('/')
def index():
    return 'GROT2 server'


@app.route('/gh-oauth', cors=cors_config)
def gh_oauth_endpoint():
    gh_code = app.current_request.query_params.get('code', None)
    if not gh_code:
        raise BadRequestError('no code')

    user_data = gh_oauth.get_user_data(
        gh_code,
        app.current_request.stage_vars.get(
            'GH_OAUTH_CLIENT_ID', os.environ.get('GH_OAUTH_CLIENT_ID')),
        app.current_request.stage_vars.get(
            'GH_OAUTH_CLIENT_SECRET', os.environ.get('GH_OAUTH_CLIENT_SECRET')),
    )
    if not user_data:
        raise BadRequestError('invalid code')

    user_id = user_data['login']
    email = user_data.get('email', '') or ''
    api_key = apigateway.get_api_key(user_id)
    if not api_key:
        api_key = apigateway.new_api_key(user_id, email)
        sdb.new_user(user_id, email, api_key)
    return {'x-api-key': api_key, 'user_id': user_id}


@app.route('/match', methods=['PUT'], api_key_required=True, cors=cors_config)
def match_put():
    api_key = app.current_request.context['identity']['apiKey']
    user_id = sdb.get_user_id(api_key)
    match_id = sdb.new_match(api_key, user_id)
    sdb.increment_total_matches(user_id)
    s3.update_hof(sdb.get_hof_data())
    return {'match_id': match_id}


@app.route('/match/{match_id}', methods=['GET'], api_key_required=True, cors=cors_config)
def match_get(match_id):
    api_key = app.current_request.context['identity']['apiKey']
    match = sdb.get_match(api_key, match_id)
    if not match:
        raise BadRequestError('invalid match_id')

    if app.debug:
        utils.print_match_state(match.get_state())

    return match.get_state()


@app.route('/match/{match_id}', methods=['POST'], api_key_required=True, cors=cors_config)
def match_post(match_id):
    api_key = app.current_request.context['identity']['apiKey']
    match = sdb.get_match(api_key, match_id)
    if not match.is_active():
        return match.get_state()

    request = app.current_request
    data = request.json_body
    try:
        row = int(data['row'])
        col = int(data['col'])
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise BadRequestError('row or col is missing or not int')

    if not 0 <= row < settings.BOARD_SIZE or not 0 <= col < settings.BOARD_SIZE:
        raise BadRequestError('row or col is out of range')

    match.start_move(row, col)
    sdb.update_match(api_key, match_id, match)
    if not match.is_active():
        sdb.increment_total_score(match.user_id, match.score)
        s3.update_hof(sdb.get_hof_data())

    if app.debug:
        print(data)
        utils.print_match_state(match.get_state())

    return match.get_state()


@app.route('/match/{match_id}/results', methods=['GET'], cors=cors_config)
def match_results_get(match_id):
    matches = sdb.get_match_results(match_id)
    matches.sort(key=lambda i: int(i['score']), reverse=True)
    return {
        'players': [
            {'user': match['user_id'], 'score': match['score']}
            for match in matches
        ]
    }