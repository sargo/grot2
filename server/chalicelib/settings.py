import os

DEBUG = os.environ.get('DEBUG') == '1'

# AWS params
APP_NAME = 'grot2-server'
API_USAGE_PLAN_ID='37vn6y'
FRONTEND_BUCKET_ID='grot2-game.lichota.pl'
CORS_ALLOW_ORGIN = 'http://grot2-game.lichota.pl'

# boto3 params
USE_SSL = DEBUG
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 10
PARAMS_VALIDATION = DEBUG
MAX_RETRIES = 5

# game parames
INIT_MOVES = 5
BOARD_SIZE = 5
PREVIEW_SIZE = BOARD_SIZE ** 2
