# GROT² server

A game server for GROT² game.

# Installation

``` bash
mkvirtualenv grot2 --python=/usr/bin/python3
pip3 install -r requirements.txt
```

# Local server
``` bash
workon grot2
DEBUG=1 chalice local --port=8080
```

# Local frontend and server
``` bash
workon grot2
cd ../frontend/static
python3 -m http.server 8080 --bind 0.0.0.0 &
cd -
DEBUG=1 CORS_ALLOW_ORGIN=http://127.0.0.1:8080 chalice local --port=8081
```

# Deployment
``` bash
workon grot2
chalice deploy --no-autogen-policy
```

# Tests

``` bash
python3 -m unittest discover
```
