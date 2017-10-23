arrow = require './arrow.coffee'
cfg = require './config.coffee'
engine = require './engine.coffee'
utils = require './utils.coffee'


class FieldWidget extends engine.Widget
    # A cirlcle with label. Circle color depends on field value (points), label shows
    # an arrow. Widget is resized and moved be Renderer.

    circle: null
    label: null
    field: null
    callback: null
    relativeScale: null

    colors:
        1: cfg.circleColor1
        2: cfg.circleColor2
        3: cfg.circleColor3
        4: cfg.circleColor4

    arrows:
        '<': 270
        '>': 90
        '^': 0
        'v': 180
        'O': 0

    constructor: (config) ->
        super
        if @field instanceof PreviewField
            radius = cfg.previewCircleRadius
            @arrow = arrow.smallArrow.clone()
        else
            radius = cfg.circleRadius
            @arrow = arrow.bigArrow.clone()

        @relativeScale = @field.relativeScale
        @circle = new Kinetic.Circle
            x: 0
            y: 0
            radius: radius
            fill: @colors[@field.value]
            transformsEnabled: 'position'

        @arrow.rotate(@arrows[@field.direction])

        @add @circle
        @add @arrow

        @scale @relativeScale

    relativeMove: (x, y) ->
        # to move widget to absolute position we have to calculate relative position
        # from current position
        @move {x: x - @x(), y: y - @y()}

    reset: () ->
        # update color and arrow after field reset
        @circle.fill(@colors[@field.value])
        angle = @arrows[@field.direction] - @arrow.rotation()
        @arrow.rotate(angle)

    setupCallback: (@callback) ->
        # setup 'onClick'
        widget = @

        @on 'forcePress', (event) ->
            widget.callback(widget.field, event)

        @on 'mousedown touchstart', (event) ->
            widget.callback(widget.field, event)


class Field
    # State of field on a board.

    x: null
    y: null
    id: null
    value: null
    direction: null
    widget: null
    board: null
    renderManager: null
    relativeScale: null
    preview: null

    constructor: (@board, @row, @col) ->
        @id = "#{@row}-#{@col}"
        @renderManager = @board.renderManager
        @relativeScale = @board.fieldRelativeScale
        @preview = @board.preview
        @reset()
        @widget = new FieldWidget
            field: @

    reset: () ->
        boardState = @board.renderManager.game.match.state.board
        @value = parseInt(boardState.points.split('\n')[@row][@col], 10)
        @direction = boardState.directions.split('\n')[@row][@col]

        if @widget?
            @widget.reset()

    getPoints: () ->
        return @value

    getFieldCenter: ()->
        # calculate positions of a field widget
        relativeRadius = cfg.circleRadius * @relativeScale
        fieldSpacing = cfg.spaceBetweenFields * @relativeScale

        centerX = fieldSpacing + relativeRadius + @col * (relativeRadius * 2 + fieldSpacing)
        centerY = fieldSpacing + relativeRadius + @row * (relativeRadius * 2 + fieldSpacing)

        centerY += cfg.previewHeight * @relativeScale

        return [centerX, centerY]

    updatePosition: (@row, @col) ->
        # update field position
        @id = "#{@row}-#{@col}"


class PreviewField extends Field
    # Field preview

    constructor: (@board, @col) ->
        @id = "preview-#{@col}"
        @renderManager = @board.renderManager
        @relativeScale = @board.fieldRelativeScale
        previewState = @board.renderManager.game.match.state.preview
        @value = parseInt(previewState.points[@col], 10)
        @direction = previewState.directions[@col]
        @widget = new FieldWidget
            field: @

    getFieldCenter: () ->
        # calculate positions of a field widget

        fieldRadius = cfg.circleRadius * @relativeScale
        previewRadius = cfg.previewCircleRadius * @relativeScale
        fieldSpacing = cfg.spaceBetweenFields * @relativeScale
        previewSpacing = cfg.spaceBetweenPreviewFields * @relativeScale
        return [
            fieldSpacing + previewRadius + @col * (previewRadius * 2 + previewSpacing),
            fieldSpacing + previewRadius
        ]

    updatePosition: (@col) ->
        @id = "preview-#{@col}"

    shift: (n) ->
        @updatePosition(@col-n)


class Preview
    # queue with next fields

    fields: []

    constructor: (@board, @size) ->
        @fields = (new PreviewField(@board, col) for col in [0..@size*2-1])

    shiftAndRefill: (n) ->
        usedFields = @fields.splice(0, n)

        for unusedField in @fields
            unusedField.shift(n)

        for usedField in usedFields
            # it will be replaced by a new widget connected to a field
            usedField.widget.destroy()

            newField = new PreviewField @board, @fields.length
            newField.widget.setOpacity 0 # will be shown by addWidgets later
            @fields.push newField
            @board.add newField.widget


class Board extends engine.Layer
    # Grid of fields.

    size: 5
    fields: []
    preview: null
    fieldRelativeScale: 0
    renderManager: null

    constructor: (config) ->
        super

        @background = new Kinetic.Rect
            width: config.width
            height: config.height
            fill: cfg.bodyColor
        @add @background

        @fieldRelativeScale = 4 / @size
        @createPreview()
        @createBoard()

        @on 'arrowPress', @handleArrowPress

    handleArrowPress: (arrowPos) ->
        row = arrowPos[0] - 1
        col = arrowPos[1] - 1

        if @fields[row] and @fields[row][col]
            @fields[row][col].widget.fire 'forcePress'

    createBoard: () ->
        # create size x size board, calculate initial value of fields
        for row in [0..@size-1]
            @fields.push (
                new Field @, row, col for col in [0..@size-1]
            )

    createPreview: () ->
        @preview = new Preview @, @size

    getNextField: (field, lastDirection=null) ->
        # returns next field in chain reaction and information is it last step in this chain reaction
        direction = if lastDirection then lastDirection else field.direction

        if direction == '<'
            if field.col == 0
                return [field, true]
            nextField = @fields[field.row][field.col - 1]

        else if direction == '>'
            if field.col == (@size-1)
                return [field, true]
            nextField = @fields[field.row][field.col + 1]

        else if direction == '^'
            if field.row == 0
                return [field, true]
            nextField = @fields[field.row - 1][field.col]

        else if direction == 'v'
            if field.row == (@size-1)
                return [field, true]
            nextField = @fields[field.row + 1][field.col]

        if nextField.direction == 'O'
            # if next was alread cleared than go further in the same direction
            return @getNextField(nextField, direction)

        return [nextField, false]

    lowerField: (field) ->
        # when chain reaction is over fields that are 'flying' should be lowered
        oldRow = field.row
        oldCol = field.col
        [nextField, lastMove] = @getNextField(field, 'v')
        newRow = nextField.row
        newCol = nextField.col

        if not lastMove
            # if not last move, than we have to take one field above
            newRow = nextField.row - 1

        if newRow == oldRow
            # no move
            return []

        # move empty field in old place
        @fields[oldRow][oldCol] = @fields[newRow][newCol]
        @fields[oldRow][oldCol].updatePosition(oldRow, oldCol)

        # move field to new place
        @fields[newRow][newCol] = field
        @fields[newRow][newCol].updatePosition(newRow, newCol)

        return [newRow, newCol]


define [], () ->
    Board: Board