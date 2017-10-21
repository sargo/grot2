"""
GROT game command line client.
"""

import argparse
import json
import os.path

from urllib.error import HTTPError
from urllib.request import urlopen, Request

import game
import utils


SERVER = 'https://api.grot2-game.lichota.pl'
TOKEN_FILE = os.path.expanduser('~/.grot2_token')

_HELP = {
    'help': 'Help on a specific subcommand',
    'register': 'Register your unique token',
    'new': 'Create new match',
    'play': 'Join match and start playing',
    'results': 'Show match results',
}


argparser = argparse.ArgumentParser()
subparsers = argparser.add_subparsers(
    dest='subcmd', help='Available commands',
)


def add_parser(name):
    return subparsers.add_parser(
        name, help=_HELP[name], description=_HELP[name]
    )


parser_help = add_parser('help')
parser_help.add_argument('subcommand')

parser_register = add_parser('register')
parser_register.add_argument('token')

parser_new_match = add_parser('new')

parser_play = add_parser('play')
parser_play.add_argument('--match_id', required=False, help='Match ID')

parser_results = add_parser('results')
parser_results.add_argument('--match_id', required=True, help='Match ID')

args = argparser.parse_args()
subcmd = args.subcmd

if not subcmd:
    argparser.parse_args(['--help'])

elif subcmd == 'help':
    argparser.parse_args([args.subcommand, '--help'])

elif subcmd == 'register':
    token = None
    if len(args.token) == 40:
        token = args.token
    elif len(args.token) == 57 and args.token.startswith('{"x-api-key": '):
        token = args.token[15:-2]

    if token:
        with open(TOKEN_FILE, 'w') as f:
            f.write(token)
        print('Token have been saved.')
    else:
        print('Invalid token!')

else:
    try:
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
    except IOError:
        token = ''
    if len(token) != 40:
        print("""No token registered.
Sign in to {} to get your token.
Use 'python3 client.py register token' before using other commands.
""".format(SERVER))

    if token:
        def new_match():
            response = utils.json_urlopen(
                '{}/match'.format(SERVER),
                method='PUT',
                headers={'x-api-key': token},
            )
            if response['code'] == 200:
                return response['json']['match_id']

        def show_results(match_id):
            response = utils.json_urlopen(
                '{}/match/{}/results'.format(SERVER, match_id))
            for i, player in enumerate(response['json']['players']):
                print('{}. {} - {}'.format(
                    i + 1, player['user'], player['score']))

        if subcmd == 'new':
            match_id = new_match()
            print('New match created with match_id: {}'.format(match_id))

        elif subcmd == 'play':
            match_id = args.match_id
            if not match_id:
                match_id = new_match()
            game.play(match_id, token, SERVER)
            show_results(match_id)

        elif subcmd == 'results':
            show_results(args.match_id)
