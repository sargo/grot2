# GROT² frontend

# Install
``` bash
npm install
```

## Build

``` bash
npm run build
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