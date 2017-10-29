request = require 'browser-request'
cfg = require './config.coffee'
utils = require './utils.coffee'


class APIMatch
    game: null
    matchId: null
    matchUrl: null
    state: {}
    headers: {}

    constructor: (matchId, @apiKey, @game) ->
        if not @apiKey
            window.location.replace('/login.html')
        else
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


window.Match = APIMatch


define () ->
    Match: APIMatch
