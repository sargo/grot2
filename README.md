# GROT²
## About
GROT² (ang. arrowhead) is a logic game about making the most valuable chains
possible!

Tap or click any field to start a chain reaction - fields will move one by one
in the direction shown by arrowheads.

Longer chains grant move bonuses (check *multiplier* parameter). Clear all
fields in a row or in a column to get extra points. Collect as many points as
possible!

## Competition
You can play this game [online](http://game.pythonfasterway.org/game.html)
but the fun part starts when your algorithm will overpower other bots!

For more details, see [grot2 client](client) readme.

## Hall of Fame
To make the results independent of randomness, all players
play in the same conditions, that is, in consecutive matches
players get the same sequence of arrows.
[Hall of Fame](http://game.pythonfasterway.org/hall-of-fame.html)
is ordered by the average points per match. The rating is
updated when you start and finish a match so play all
matches to the end to keep high average!

## Credits

GROT² is based on MIT licensed [GROT game](http://grot.hackathons.stxnext.pl/)
by [STX Next](https://stxnext.com/).

GROT² server use [Chalice](https://chalice.readthedocs.io) framework and run
on AWS Lambda.

GROT² online game use [KineticJS](http://kineticjs.com) and HTML5 Canvas.
