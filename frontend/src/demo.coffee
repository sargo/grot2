cfg = require './config.coffee'
utils = require './utils.coffee'


class DemoMatch
    game: null
    state: {}

    constructor: (matchId, apiKey, @game) ->
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
        ), 0

    beforeSync: () ->
        @state.score = @game.score
        @state.moves = @game.moves
        @state['bonus-multiplier'] = 100 / (@game.score + 200)

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
                    setCharAt('points', row, col, pp[0])
                    pp = pp.substr(1) + utils.randomChoice('1111222334')
                    setCharAt('directions', row, col, pd[0])
                    pd = pd.substr(1) + utils.randomChoice('<>^v')
                else
                    setCharAt('points', row, col, field.value)
                    setCharAt('directions', row, col, field.direction)

        @state.preview.points = pp
        @state.preview.directions = pd

    postMove: (row, col) ->


window.Match = DemoMatch


define () ->
    Match: DemoMatch
