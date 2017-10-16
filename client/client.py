"""
GROT game command line client.
"""

import argparse
import json
import os.path

from urllib.error import HTTPError
from urllib.request import urlopen, Request

import game


SERVER = 'api.game.pythonfasterway.org'
TOKEN_FILE = os.path.expanduser('~/.grot_token')

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
    with open(TOKEN_FILE, 'w') as f:
        f.write(args.token)
    print('Token have been saved.')

else:
    try:
        with open(TOKEN_FILE) as f:
            token = f.read().strip()
    except IOError:
        token = ''
    if len(token) != 36:
        print("""No token registered.
Sign in to https://{} to get your token.
Use 'python3 client.py register token' before using other commands.
""".format(SERVER))

    if token:
        def new_match():
            req = Request(
                url='https://{}/match?token={}'.format(SERVER, token),
                method='PUT',
            )

            try:
                resp = urlopen(req)
            except HTTPError as e:
                print(e.read().decode('utf8'))
                raise

            data = json.loads(resp.read().decode('utf8', 'ignore'))
            return data['match_id']

        def show_results(match_id):
            req = Request(
                url='https://{}/match/{}/results?token={}'.format(
                    SERVER, match_id, token
                ),
                headers={'Accept': 'application/json'},
            )
            data = json.loads(urlopen(req).read().decode('utf8'))
            for i, player in enumerate(data['players']):
                print('{}. {} - {}'.format(
                    i + 1, player['login'], player['score']))

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
