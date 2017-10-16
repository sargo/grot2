# grot2 frontend

> GROT 2 game

## Build site

``` bash
cd src
coffee --join ../static/js/grot2.js --compile -- config.coffee \
       engine.coffee api.coffee control-bars.coffee board.coffee \
       menu.coffee game.coffee
```

## Update site

``` bash
aws s3 cp index.html s3://game.pythonfasterway.org \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp game.html s3://game.pythonfasterway.org \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp static s3://game.pythonfasterway.org/static --recursive \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
```