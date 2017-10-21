game = require('./game.coffee')
cfg = require('./config.coffee')


window.game = new game.Game
document.body.style.cssText = 'background-color: ' + cfg.bodyColor + '; margin: 0; padding: 0;'
