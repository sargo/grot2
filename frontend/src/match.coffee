request = require 'browser-request'
cfg = require './config.coffee'
utils = require './utils.coffee'


class Match
    game: null
    matchId: null
    matchUrl: null
    state: {}
    headers: {}

    constructor: (matchId, @apiKey, @game) ->
        @headers = {'X-Api-Key': @apiKey}
        if matchId?
            @setMatchId(matchId)
            @getState()
        else
            @newMatch()

    update: (data) ->
        @state = data

    setMatchId: (@matchId) ->
        @matchUrl = cfg.serverUrl + '/match/' + @matchId

    newMatch: () ->
        matchUrl = cfg.serverUrl + '/match'
        request.put
            uri: matchUrl
            json: true
            headers: @headers
            (err, r, body) =>
                @setMatchId(body['match_id'])
                @getState()

    getState: () ->
        request.get
            uri: @matchUrl,
            json: true
            headers: @headers
            (err, r, body) =>
                @state = body
                @game.init()

    postMove: (row, col) ->
        request.post
            uri: @matchUrl
            body:
                row: row
                col: col
            json: true
            headers: @headers
            (err, r, body) =>
                @state = body

    beforeSync: () ->


class DemoMatch
    game: null
    state: {}

    constructor: (@game) ->
        size = 5
        @state =
            score: 0
            moves: 5
            preview:
                points: (
                    utils.randomChoice('1111222334') for row in [0..size*size-1]
                ).join('')
                directions: (
                    utils.randomChoice('<>^v') for row in [0..size*size-1]
                ).join('')
            board:
                points: (
                    (utils.randomChoice('1111222334') for row in [0..size-1])
                    .join('') for col in [0..size-1]
                ).join('\n')
                directions: (
                    (utils.randomChoice('<>^v') for row in [0..size-1])
                    .join('') for col in [0..size-1]
                ).join('\n')

        setTimeout ( ->
            @game.init()
        ), 1000

    beforeSync: () ->
        @state.score = @game.score
        @state.moves = @game.moves
        pp = @state.preview.points
        pd = @state.preview.directions

        setCharAt = (attr, row, col, chr) =>
            str = @state.board[attr]
            index = row * (@game.boardSize + 1) + col
            @state.board[attr] = str.substr(0, index) + chr + str.substr(index+1)

        for row in [0..@game.boardSize-1]
            for col in [0..@game.boardSize-1]
                field = @game.board.fields[row][col]
                if field.direction == 'O'
                    setCharAt('points', row, col, parseInt(pp[0]))
                    pp = pp.substr(1) + utils.randomChoice('1111222334')
                    setCharAt('directions', row, col, pd[0])
                    pd = pd.substr(1) + utils.randomChoice('<>^v')
                else
                    setCharAt('points', row, col, field.points)
                    setCharAt('directions', row, col, field.direction)

        @state.preview.points = pp
        @state.preview.directions = pd

    postMove: (row, col) ->


define () ->
    Match: Match
    DemoMatch: DemoMatch