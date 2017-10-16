# GROT - html5 canvas game

window.TWEEN_DURATION = (10 - cfg.defaultSpeed) * cfg.tweenDurationUnit
window.delay1s = (func) -> setTimeout func, 1000

window.randomChoice = (values) ->
    # http://rosettacode.org/wiki/Pick_random_element#CoffeeScript
    return values[Math.floor(Math.random() * values.length)]


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


class RenderManager extends GrotEngine.RenderManager
    # Manage canvas and widgets

    board: null
    stage: null
    barsLayer: null
    animLayer: null
    game: null
    topBarWidget: null
    menuOverlay: null

    constructor: (@boardSize, @showPreview, @game) ->
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
        previewHeight = if @showPreview then cfg.previewHeight else 0
        @barsLayer = new GrotEngine.Layer
            width: 600
            height: 900+previewHeight
            margins: {x: 0, y: 0}
            renderManager: @

        @board = new Grot.Board
            size: @boardSize
            showPreview: @showPreview
            renderManager: @
            margins: {x: 0, y: 180}
            width: 600
            height: 600+previewHeight

        @game.board = @board

        # create next layers only for animations (better performance)
        @animLayer = new GrotEngine.Layer
            hitGraphEnabled: false
            margins: {x: 0, y: 180}
            width: 600
            height: 600+previewHeight
            renderManager: @

        #create overlay for menu/gameover/help view
        @menuOverlay = new Grot.MenuOverlay
            width: 600
            height: 900+previewHeight
            margins: {x: 0, y: 0}
            renderManager: @
            showPreview: @showPreview

    addWidgets: ->
        @topBarWidget = new Grot.TopBarWidget
            game: @game
            showPreview: @showPreview
        @bottomBarWidget = new Grot.BottomBarWidget
            game: @game
            showPreview: @showPreview

        # add board fields to the layer
        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                @board.add @board.fields[x][y].widget

        # add preview fields to the layer
        if @showPreview
            for x in [0..@board.size*2-1]
                @board.preview.fields[x].widget.setOpacity 1
                @board.add @board.preview.fields[x].widget

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

        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                field = @board.fields[x][y]
                [centerX, centerY] = field.getFieldCenter()
                widget = field.widget
                widget.relativeMove centerX, centerY
                if not widget.callback?
                    # set 'onClick' callback
                    widget.setupCallback(@startMove)

        if @showPreview
            for x in [0..@board.size*2-1]
                field = @board.preview.fields[x]
                [centerX, centerY] = field.getFieldCenter()
                widget = field.widget
                widget.relativeMove centerX, centerY

    listening: (state) ->
        # toggle listening for event on all field widgets
        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                @board.fields[x][y].widget.listening(state)
        @board.drawHit()

    startMove: (field, event) =>
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
        startField.direction = 'none'
        @movePoints += startField.getPoints()
        @moveLength += 1

        # move field to animLayer until animation is finished
        @moveFieldToLayer(startField, @animLayer)

        tween = new Kinetic.Tween
            node: startField.widget
            duration: window.TWEEN_DURATION
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
        for x in [0..@board.size-1]
            isEmptyColumn = true
            for y in [0..@board.size-1]
                if @board.fields[x][y].direction != 'none'
                    isEmptyColumn = false

            if isEmptyColumn
                @movePoints += @board.size * 10

        for y in [0..@board.size-1]
            isEmptyRow = true
            for x in [0..@board.size-1]
                if @board.fields[x][y].direction != 'none'
                    isEmptyRow = false

            if isEmptyRow
                @movePoints += @board.size * 10

        @lowerFields()

    lowerFields: () ->
        # lower fields (gravity)
        tweens = []
        for y in [@board.size-2..0]
            for x in [0..@board.size-1]
                field = @board.fields[x][y]
                if field.direction != 'none'
                    result = @board.lowerField(field)
                    if result.length == 2
                        [newX, newY] = result
                        [centerX, centerY] = field.getFieldCenter()
                        # move field to animLayer until animation is finished
                        @moveFieldToLayer(field, @animLayer)

                        tweens.push new Kinetic.Tween
                            node: field.widget
                            easing: Kinetic.Easings.BounceEaseOut,
                            duration: window.TWEEN_DURATION
                            x: centerX
                            y: centerY
                            onFinish: =>
                                `this.destroy()`

        if tweens.length > 0
            tweens[0].onFinish = () =>
                if @showPreview
                    @movePreviewToEmptyFields()
                else
                    @fillEmptyFields()
                `this.destroy()`

            for tween in tweens
                tween.play()
        else
            if @showPreview
                @movePreviewToEmptyFields()
            else
                @fillEmptyFields()

    fillEmptyFields: () ->
        # reset fields in empty places and show them
        tweens = []
        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                field = @board.fields[x][y]
                if field.direction == 'none'
                    field.reset()

                    # move field to animLayer until animation is finished
                    @moveFieldToLayer(field, @animLayer)

                    tweens.push new Kinetic.Tween
                        node: field.widget
                        opacity: 1
                        duration: window.TWEEN_DURATION
                        onFinish: =>
                            `this.destroy()`

        @stage.fire 'onStageUpdated'

        if tweens.length > 0
            tweens[0].onFinish = () =>
                @finishMove()
                `this.destroy()`

            for tween in tweens
                tween.play()
        else
            @finishMove()

    movePreviewToEmptyFields: () ->
        # move preview field to empty places
        tweens = []
        previewIndex = 0
        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                field = @board.fields[x][y]
                if field.direction == 'none'
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
                            duration: window.TWEEN_DURATION
                            onFinish: =>
                                `this.destroy()`

        # shift rest of preview to the left
        if previewIndex < @board.size*2-1
            for x in [previewIndex..@board.size*2-1]
                previewField = @board.preview.fields[x]
                destinationField = @board.preview.fields[x-previewIndex]
                [centerX, centerY] = destinationField.getFieldCenter()

                @moveFieldToLayer(previewField, @animLayer)

                tweens.push new Kinetic.Tween
                    node: previewField.widget
                    x: centerX
                    y: centerY
                    duration: window.TWEEN_DURATION
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

        for x in [0..@board.size-1]
            for y in [0..@board.size-1]
                field = @board.fields[x][y]
                if field.direction == 'none'
                    field.reset() # this will destroy preview widget
                    field.widget.setOpacity 1

        @stage.fire 'onStageUpdated'

        # show new preview fields on the end of preview queue
        for x in [0..@board.size*2-1]
            previewField = @board.preview.fields[x]
            if previewField.widget.getOpacity() == 0
                tweens.push new Kinetic.Tween
                    node: previewField.widget
                    opacity: 1
                    duration: window.TWEEN_DURATION
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

        # multiplier depends on current score, more points you have then
        # multiplier is smaller so longer path you have to create to get moves bonus
        multiplier = 100 / (@game.score + 200)
        @game.movesDiff = Math.floor(@moveLength * multiplier)
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


class Game extends GrotEngine.Game
    board: null
    score: 0
    scoreDiff: 0
    moves: 5
    movesDiff: 0
    renderManager: null

    constructor: () ->
        super

        qs = new QueryString
        qsSize = parseInt(qs.get('size'))
        qsPreview = qs.get('preview') is 'true'
        qsSpeed = parseInt(qs.get('speed'))

        boardSize = if cfg.customBoardSize and qsSize
        then qsSize else cfg.defaultBoardSize

        showPreview = if cfg.customShowPreview and qsPreview
        then qsPreview else cfg.showPreview

        speed = if cfg.customSpeed and qsSpeed and qsSpeed > 0 and qsSpeed < 10
        then qsSpeed else cfg.defaultSpeed
        window.TWEEN_DURATION = (10 - speed) * cfg.tweenDurationUnit

        @renderManager = new RenderManager boardSize, showPreview, @


document.body.style.cssText = 'background-color: ' + cfg.bodyColor + '; margin: 0; padding: 0;'
window.game = game = new Game()
