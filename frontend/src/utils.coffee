cfg = require './config.coffee'


define [], () ->
    delay1s: (func) -> setTimeout func, 1000

    randomChoice: (values) ->
        # http://rosettacode.org/wiki/Pick_random_element#CoffeeScript
        return values[Math.floor(Math.random() * values.length)]
