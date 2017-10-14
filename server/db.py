
import random
import textwrap

import boto3
import multidict

from grotlogic.board import Board
from grotlogic.match import Match
from grotlogic.player import Player
from grotlogic.random import DenseStateRandom
import settings


client = boto3.client('sdb')


def init_db():
    domains = client.list_domains().get('DomainNames', [])
    if 'matches' not in domains:
        client.create_domain(DomainName='matches')


def clear_db():
    client.delete_domain(DomainName='matches')


def _parse_attrs(data):
    return multidict.MultiDict(((i['Name'], i['Value']) for i in data))


def _split_long(text, attr):
    return [
        {'Name': '{}_{}'.format(attr, i), 'Value': line, 'Replace': True}
        for i, line in enumerate(textwrap.wrap(text, 1020, drop_whitespace=False))
    ]


def _join_long(attrs, attr):
    lines = []
    i = 0
    while '{}_{}'.format(attr, i) in attrs:
        lines.append(attrs['{}_{}'.format(attr, i)])
        i += 1
    return ''.join(lines)


def _insert_match(match_id, user_id, seed, random_state):
    match_key = user_id + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'match_key', 'Value': match_key, 'Replace': True},
            {'Name': 'match_id', 'Value': match_id, 'Replace': True},
            {'Name': 'user_id', 'Value': user_id, 'Replace': True},
            {'Name': 'seed', 'Value': seed, 'Replace': True},
            {'Name': 'score', 'Value': '0', 'Replace': True},
            {'Name': 'moves', 'Value': str(settings.INIT_MOVES), 'Replace': True},
        ] + _split_long(random_state, 'random_state'),
        Expected={'Name': 'match_key', 'Exists': False},
    )


def _get_match_obj(match_state):
    attrs = _parse_attrs(match_state['Attributes'])
    random_state = _join_long(attrs, 'random_state')
    return Match(
        Player(attrs['user_id']),
        Board.from_random_state(random_state),
        int(attrs['score']),
        int(attrs['moves']),
    )


def new_match(user_id):
    # get last match is exist
    response = client.select(
        SelectExpression="select * from matches where user_id='{}' and match_id is not null order by match_id desc limit 1".format(user_id),
        ConsistentRead=True,
    )
    matches = response.get('Items')
    if matches:
        # increment match_id
        attrs = _parse_attrs(matches[0]['Attributes'])
        new_match_id = str(int(attrs['match_id']) + 1)
    else:
        new_match_id = '0'

    # search for other users' matches
    response = client.select(
        SelectExpression="select * from matches where match_id='{}' limit 1".format(new_match_id),
        ConsistentRead=True,
    )
    matches = response.get('Items')
    if matches:
        # extract seed
        seed = int(_parse_attrs(matches[0]['Attributes'])['seed'])
    else:
        seed = random.getrandbits(128)

    random_state = DenseStateRandom(seed).getstate()
    try:
        _insert_match(new_match_id, user_id, str(seed), random_state)
    except:
        import pdb; pdb.set_trace()
        raise

    return new_match_id


def get_match(user_id, match_id):
    response = client.select(
        SelectExpression="select * from matches where match_key='{}_{}' limit 1".format(user_id, match_id),
        ConsistentRead=True,
    )
    matches = response.get('Items')
    if matches:
        return _get_match_obj(matches[0])


def update_match(user_id, match_id, match):
    match_key = user_id + '_' + match_id
    client.put_attributes(
        DomainName='matches',
        ItemName=match_key,
        Attributes=[
            {'Name': 'score', 'Value': str(match.score), 'Replace': True},
            {'Name': 'moves', 'Value': str(match.moves), 'Replace': True},
        ] + _split_long( match.board.random.getstate(), 'random_state'),
        Expected={'Name': 'score', 'Value': str(match.old_score)},
    )


def get_all_matches(match_id):
    response = client.select(
        SelectExpression="select * from matches where match_id='{}'".format(match_id),
        ConsistentRead=True,
    )
    matches = response.get('Items', [])
    return [_parse_attrs(match['Attributes']) for match in matches]


if __name__ == '__main__':
    clear_db()
    init_db()
