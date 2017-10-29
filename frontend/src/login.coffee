request = require 'browser-request'
cfg = require('./config.coffee')
utils = require './utils.coffee'


class Login

    constructor: () ->
        qs = new utils.QueryString
        qsCode = qs.get('code')
        if qsCode
            request.get
                uri: cfg.serverUrl + '/gh-oauth?code=' + qsCode,
                json: true
                (err, r, body) =>
                    document.getElementById('spinner').remove()
                    if err
                        document.getElementById('wrap').innerHTML = 'Error: ' + err
                        throw err

                    apiKey = body['x-api-key']
                    userId = body['user_id']
                    if apiKey?
                        localStorage.setItem('api_key', apiKey)
                        localStorage.setItem('user_id', userId)
                        document.getElementById('user_id').innerHTML = userId
                        document.getElementById('api_key').innerHTML = apiKey
                        document.getElementById('signed-in').style.display = 'block'
                    else
                        document.getElementById('content').innerHTML = 'Unexpected error'
        else
            apiKey = localStorage.getItem('api_key')
            userId = localStorage.getItem('user_id')
            document.getElementById('spinner').remove()
            if apiKey?
                document.getElementById('user_id').innerHTML = userId
                document.getElementById('api_key').innerHTML = apiKey
                document.getElementById('signed-in').style.display = 'block'
            else
                document.getElementById('sign-in').style.display = 'block'


window.login = new Login
