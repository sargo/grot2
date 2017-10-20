# GROT² frontend

## Build

``` bash
cd src
coffee --join ../static/js/grot2.js --compile -- config.coffee \
       engine.coffee arrow.coffee control-bars.coffee board.coffee \
       menu.coffee game.coffee
```

## Update

``` bash
aws s3 cp index.html s3://grot2-game.lichota.pl \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp game.html s3://grot2-game.lichota.pl \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp error.html s3://grot2-game.lichota.pl \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
aws s3 cp static s3://grot2-game.lichota.pl/static --recursive \
    --grants read=uri=http://acs.amazonaws.com/groups/global/AllUsers
```