define () ->
  ###
  Board size
  ###
  defaultBoardSize: 5

  baseScale: 1
  baseWindowSize:
    width: 1600
    height: 900

  ###
  Enables or disables possibility to pass
  initial board size as ?size=x param
  ###
  customBoardSize: false

  ###
  Display row with fields that will replace empty fields after move
  ###
  showPreview: true

  ###
  Enables or disables possibility to pass
  ?preview=yes param to enable preview
  ###
  customShowPreview: false

  ###
  FieldWidget(Circle) settings
  ###
  circleColor1: '#868788'
  circleColor2: '#ffec00'
  circleColor3: '#8d198f'
  circleColor4: '#00968f'

  circleRadius: 65
  spaceBetweenFields: 16

  previewHeight: 80
  previewCircleRadius: 32
  spaceBetweenPreviewFields: 8

  ###
  Arrow settings
  ###
  arrowColor: '#ffffff'

  ###
  Tween duration settings

  Enables or disables possibility to pass
  ?speed=1..9 param to configure animation speed
  ###
  customSpeed: true

  defaultSpeed: 6
  tweenDurationUnit: 0.1
  tweenDuration: (10 - @defaultSpeed) * @tweenDurationUnit

  ###
  Font settings
  ###
  fontScoMovColor: '#868788'
  fontScoMovNumColor: '#00968f'
  fontMenuColor: '#ffffff'
  fontFamily: 'Lato'
  fontScoMovSize: 46
  fontRestSize: 38
  fontStyle: 'Bold'

  ###
  Background color settings
  ###
  bodyColor: '#ffffff'
  overlayColor: '#333333'
  overlayBodyColor: '#484848'

  ###
  Urls settings
  ###
  scoreBoardLink: 'http://grot2-game.lichota.pl/hall-of-fame/'

  ###
  Help description
  ###
  helpDesc: ' This logic game is about making the most\n
            valuable chains possible!\n\n
            Tap or click any field to start a chain\n
            reaction - fields will move one by one in\n
            the direction shown by the arrowheads.\n\n
            Longer chains grant move bonuses.\n
            Clear all fields in a row or in a column\n
            to get extra points.\n\n
            Collect as many points as possible!'

  ###
  About description
  ###
  aboutDesc: ' Source code\n
              https://github.com/sargo/grot2'

  aboutVer: ' v2.0'
