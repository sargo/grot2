# GROT - html5 canvas game
cfg = require './config.coffee'
engine = require './engine.coffee'
board = require './board.coffee'
menu = require './menu.coffee'
ctrl_bars = require './control-bars.coffee'
utils = require './utils.coffee'


class RenderManager extends engine.RenderManager
    # Manage canvas and widgets

    board: null
    stage: null
    barsLayer: null
    animLayer: null
    game: null
    topBarWidget: null
    menuOverlay: null

    constructor: (@boardSize, @game) ->
        [width, height] = @getWindowSize()
        @currentScale = @calculateScaleUnit()

        @addLayers()
        @addWidgets()

        @stage = new Kinetic.Stage
            container: 'wrap'
            width: width
            height: height - 4

        @stage.on 'onStageUpdated', @onStageUpdated.bind(@)
        @stage.on 'blurBoardStuff', @blurBoardStuff.bind(@)
        @stage.on 'normalizeBoardStuff', @normalizeBoardStuff.bind(@)

        @stage.fire 'onStageUpdated'

        @stage.add @board
        @stage.add @barsLayer
        @stage.add @animLayer
        @stage.add @menuOverlay

        @barsLayer.filters [Kinetic.Filters.Blur]
        @board.filters [Kinetic.Filters.Blur]

        super

        layers = @stage.getLayers()
        for layer in layers
            layer.fire 'update'

        @stage.fire 'ready'

    addLayers: ->
        @barsLayer = new engine.Layer
            width: 600
            height: 900+cfg.previewHeight
            margins: {x: 0, y: 0}
            renderManager: @

        @board = new board.Board
            size: @boardSize
            renderManager: @
            margins: {x: 0, y: 180}
            width: 600
            height: 600+cfg.previewHeight

        @game.board = @board

        # create next layers only for animations (better performance)
        @animLayer = new engine.Layer
            hitGraphEnabled: false
            margins: {x: 0, y: 180}
            width: 600
            height: 600+cfg.previewHeight
            renderManager: @

        #create overlay for menu/gameover/help view
        @menuOverlay = new menu.MenuOverlay
            width: 600
            height: 900+cfg.previewHeight
            margins: {x: 0, y: 0}
            renderManager: @

    addWidgets: ->
        @topBarWidget = new ctrl_bars.TopBarWidget
            game: @game
        @bottomBarWidget = new ctrl_bars.BottomBarWidget
            game: @game

        # add board fields to the layer
        for row in [0..@board.size-1]
            for col in [0..@board.size-1]
                @board.add @board.fields[row][col].widget

        # add preview fields to the layer
        for col in [0..@board.size*2-1]
            @board.preview.fields[col].widget.setOpacity 1
            @board.add @board.preview.fields[col].widget

        # add bar widgets to a barsLayer

        @barsLayer.add @topBarWidget
        @barsLayer.add @bottomBarWidget

    normalizeBoardStuff: ->
        @barsLayer.blurRadius 0
        @board.blurRadius 0
        @board.clearCache()
        @barsLayer.clearCache()
        @barsLayer.batchDraw()
        @board.batchDraw()

    blurBoardStuff: ->
        @barsLayer.cache()
        @board.cache()
        @barsLayer.blurRadius 10
        @board.blurRadius 10
        @barsLayer.batchDraw()
        @board.batchDraw()

    moveFieldToLayer: (field, toLayer) ->
        # moves field to new layer
        fromLayer = field.widget.getLayer()
        field.widget.moveTo(toLayer)
        # refresh layers cache
        fromLayer.draw()
        toLayer.draw()

    onStageUpdated: () ->
        # Resize and set positions of widgets

        for row in [0..@board.size-1]
            for col in [0..@board.size-1]
                field = @board.fields[row][col]
                [centerX, centerY] = field.getFieldCenter()
                widget = field.widget
                widget.rePosition()
                widget.relativeMove centerX, centerY
                if not widget.callback?
                    # set 'onClick' callback
                    widget.setupCallback(@startMove)

        for col in [0..@board.size*2-1]
            field = @board.preview.fields[col]
            [centerX, centerY] = field.getFieldCenter()
            widget = field.widget
            widget.rePosition()
            widget.relativeMove centerX, centerY

    listening: (state) ->
        # toggle listening for event on all field widgets
        for row in [0..@board.size-1]
            for col in [0..@board.size-1]
                @board.fields[row][col].widget.listening(state)
        @board.drawHit()

    startMove: (field, event) =>
        # we have to save multiplier before sending move to api server because
        # it will be overwritten as soon as server will respond
        @multiplier = @game.match.state['bonus-multiplier']
        @game.match.postMove(field.row, field.col)

        # deactivate listening until animation is finished
        @listening(false)
        @game.moves -= 1
        @game.scoreDiff = 0
        @game.movesDiff = 0
        @topBarWidget.update()

        @movePoints = 0
        @moveLength = 0
        # start chain reaction
        @moveToNextField(field)

    moveToNextField: (startField) ->
        # one step in chain reaction
        [nextField, lastMove] = @board.getNextField(startField)
        [centerX, centerY] = nextField.getFieldCenter()
        startField.direction = 'O'
        @movePoints += startField.getPoints()
        @moveLength += 1

        # move field to animLayer until animation is finished
        @moveFieldToLayer(startField, @animLayer)

        tween = new Kinetic.Tween
            node: startField.widget
            duration: cfg.tweenDuration
            x: centerX
            y: centerY
            opacity: 0

            onFinish: =>
                if lastMove
                    @checkEmptyLines()
                else
                    @moveToNextField(nextField)

                `this.destroy()`

        tween.play()

    checkEmptyLines: () ->
        # count empty rows and columns and give extra points
        for row in [0..@board.size-1]
            isEmptyRow = true
            for col in [0..@board.size-1]
                if @board.fields[row][col].direction != 'O'
                    isEmptyRow = false

            if isEmptyRow
                @movePoints += @board.size * 10

        for col in [0..@board.size-1]
            isEmptyColumn = true
            for row in [0..@board.size-1]
                if @board.fields[row][col].direction != 'O'
                    isEmptyColumn = false

            if isEmptyColumn
                @movePoints += @board.size * 10

        @lowerFields()

    lowerFields: () ->
        # lower fields (gravity)
        tweens = []
        for row in [@board.size-2..0]
            for col in [0..@board.size-1]
                field = @board.fields[row][col]
                if field.direction != 'o'
                    result = @board.lowerField(field)
                    if result.length == 2
                        [centerX, centerY] = field.getFieldCenter()
                        # move field to animLayer until animation is finished
                        @moveFieldToLayer(field, @animLayer)

                        tweens.push new Kinetic.Tween
                            node: field.widget
                            easing: Kinetic.Easings.BounceEaseOut,
                            duration: cfg.tweenDuration
                            x: centerX
                            y: centerY
                            onFinish: =>
                                `this.destroy()`

        if tweens.length > 0
            tweens[0].onFinish = () =>
                @movePreviewToEmptyFields()
                `this.destroy()`

            for tween in tweens
                tween.play()
        else
            @movePreviewToEmptyFields()

    movePreviewToEmptyFields: () ->
        @game.match.beforeSync()

        # move preview field to empty places
        tweens = []
        previewIndex = 0
        for row in [0..@board.size-1]
            for col in [0..@board.size-1]
                field = @board.fields[row][col]
                if field.direction == 'O'
                    [centerX, centerY] = field.getFieldCenter()

                    previewField = @board.preview.fields[previewIndex]
                    previewIndex += 1
                    if previewField?
                        # move field to animLayer until animation is finished
                        @moveFieldToLayer(previewField, @animLayer)

                        tweens.push new Kinetic.Tween
                            node: previewField.widget
                            x: centerX
                            y: centerY
                            scaleX: 2
                            scaleY: 2
                            duration: cfg.tweenDuration
                            onFinish: =>
                                `this.destroy()`

        # shift rest of preview to the left
        if previewIndex < @board.size*2-1
            for col in [previewIndex..@board.size*2-1]
                previewField = @board.preview.fields[col]
                destinationField = @board.preview.fields[col-previewIndex]
                [centerX, centerY] = destinationField.getFieldCenter()

                @moveFieldToLayer(previewField, @animLayer)

                tweens.push new Kinetic.Tween
                    node: previewField.widget
                    x: centerX
                    y: centerY
                    duration: cfg.tweenDuration
                    onFinish: =>
                        `this.destroy()`

        if tweens.length > 0
            tweens[0].onFinish = () =>
                @updatePreview()
                `this.destroy()`

            for tween in tweens
                tween.play()
        else
            @updatePreview()

    updatePreview: () ->
        # move values and direction from preview to field
        tweens = []

        for col in [0..@board.size-1]
            for row in [0..@board.size-1]
                field = @board.fields[row][col]
                if field.direction == 'O'
                    field.reset() # this will destroy preview widget
                    field.widget.setOpacity 1

        # remove from preview fields moved to board and add new one
        @board.preview.shiftAndRefill(@moveLength)

        @stage.fire 'onStageUpdated'

        # show new preview fields on the end of preview queue
        for col in [0..@board.size*2-1]
            previewField = @board.preview.fields[col]
            if previewField.widget.getOpacity() == 0
                tweens.push new Kinetic.Tween
                    node: previewField.widget
                    opacity: 1
                    duration: cfg.tweenDuration
                    onFinish: =>
                        `this.destroy()`

        if tweens.length > 0
            tweens[0].onFinish = () =>
                @finishMove()
                `this.destroy()`

            for tween in tweens
                tween.play()
        else
            @finishMove()

    gameOver: () ->
        # return message with scored result
        @menuOverlay.fire 'showGameOver', @game.score
        @stage.fire 'gameOver'

    finishMove: () ->
        # update game score

        @game.score += @movePoints
        @game.scoreDiff = @movePoints

        @game.movesDiff = Math.floor(@moveLength * @multiplier)
        @game.moves += @game.movesDiff
        @topBarWidget.update()

        fields = (attrs.field for attrs in @animLayer.children)
        for field in fields
            @moveFieldToLayer(field, @board)

        if @game.moves > 0
            # reactivate listening
            @listening(true)
            @stage.fire 'moveCompleted'
        else
            # game over
            @stage.fire 'moveCompleted'
            @gameOver(@game)


class Game extends engine.Game
    match: null
    boardSize: null
    score: 0
    scoreDiff: 0
    moves: 5
    movesDiff: 0
    renderManager: null

    constructor: () ->
        super

        qs = new utils.QueryString
        qsSize = parseInt(qs.get('size'))
        qsPreview = qs.get('preview') is 'true'
        qsSpeed = parseInt(qs.get('speed'))

        @boardSize = if cfg.customBoardSize and qsSize
        then qsSize else cfg.defaultBoardSize

        speed = if cfg.customSpeed and qsSpeed and qsSpeed > 0 and qsSpeed < 10
        then qsSpeed else cfg.defaultSpeed
        cfg.tweenDuration = (10 - speed) * cfg.tweenDurationUnit

        apiKey = localStorage.getItem('api_key')
        qsMatchId = qs.get('match_id')
        @match = new window.Match qsMatchId, apiKey, @

    init: () ->
        @score = @match.state.score
        @moves = @match.state.moves
        @renderManager = new RenderManager @boardSize, @
        if @moves == 0
            @renderManager.gameOver()

    update: () ->
        console.log(@renderManager)


define [], () ->
    Game: Game