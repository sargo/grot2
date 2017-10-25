cfg = require './config.coffee'


class QueryString
    # Provide easy access to QueryString data
    # https://gist.github.com/greystate/1274961

    constructor: (@queryString) ->
        @queryString or= window.document.location.search?.substr 1
        @variables = @queryString.split '&'
        @pairs = ([key, value] = pair.split '=' for pair in @variables)

    get: (name) ->
        for [key, value] in @pairs
            return value if key is name


define [], () ->
    QueryString: QueryString
    delay1s: (func) -> setTimeout func, 1000
    randomChoice: (values) ->
        # http://rosettacode.org/wiki/Pick_random_element#CoffeeScript
        return values[Math.floor(Math.random() * values.length)]
