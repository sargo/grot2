# GROT² game client

A client that simplifys development of a bot for GROT² game.

# Installation

Download GROT² client
``` bash
wget https://github.com/sargo/grot2/archive/master.zip
unzip -j master.zip grot2-master/client/* -d grot2-client
cd grot2-client
```

# Sign-Up
To play GROT² you have to sign-up with GitHub OAuth by opening:

https://github.com/login/oauth/authorize?client_id=4ba20fc056b74df39cc0&scope=user:email

After authorization you will be redrected to a game server which will
generate a new API key. This API key have to be registered in the client:

``` bash
python3 client.py register your-unique-api-key
```

# Play

``` bash
python3 client.py play
```

If you haven't finished a match you can always go back and play it by
providing *match_id*:

``` bash
python3 client.py play --match-id=<int>
```

# Help

Check other options by running:

``` bash
python3 client.py --help
```

# API

At first install `httpie`, a command line tool to visualize API calls:
``` bash
pip3 install httpie
```

Create a new match:
``` bash
http PUT https://api.grot2-game.lichota.pl/match X-Api-Key:`cat ~/.grot2_token`
```

Get match state:
``` bash
http https://api.grot2-game.lichota.pl/match/0 X-Api-Key:`cat ~/.grot2_token`
```

Make a move:
``` bash
http POST https://api.grot2-game.lichota.pl/match/0 X-Api-Key:`cat ~/.grot2_token` x=0 y=0
```

Show match results:
``` bash
http https://api.grot2-game.lichota.pl/match/0/results
```