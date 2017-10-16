arrowCommands = [
        y: -12.40625
        x: -3.38671875
        type: 'M'
    ,
        y1: -8.94921875
        x: -9.71484375
        x1: -6.521484375
        type: 'Q'
        y: -5.4921875
    ,
        y1: -2.03515625
        x: -16.365234375
        x1: -12.908203125
        type: 'Q'
        y: 1.392578125
    ,
        y1: 1.626953125
        x: -16.8779296875
        x1: -16.599609375
        type: 'Q'
        y: 1.7294921875
    ,
        y1: 1.83203125
        x: -17.5517578125
        x1: -17.15625
        type: 'Q'
        y: 1.685546875
    ,
        y1: 1.5390625
        x: -18.50390625
        x1: -17.947265625
        type: 'Q'
        y: 1.1142578125
    ,
        y1: 0.689453125
        x: -19.880859375
        x1: -19.060546875
        type: 'Q'
        y: -0.130859375
    ,
        y1: -0.921875
        x: -21.0380859375
        x1: -20.642578125
        type: 'Q'
        y: -1.44921875
    ,
        y1: -1.9765625
        x: -21.55078125
        x1: -21.43359375
        type: 'Q'
        y: -2.3427734375
    ,
        y1: -2.708984375
        x: -21.580078125
        x1: -21.66796875
        type: 'Q'
        y: -2.97265625
    ,
        y1: -3.236328125
        x: -21.2578125
        x1: -21.4921875
        type: 'Q'
        y: -3.470703125
    ,
        y: -22.748046875
        x: -1.98046875
        type: 'L'
    ,
        y1: -23.1875
        x: -1.04296875
        x1: -1.541015625
        type: 'Q'
        y: -23.48046875
    ,
        y1: -23.7734375
        x: 0.158203125
        x1: -0.544921875
        type: 'Q'
        y: -23.7734375
    ,
        y1: -23.7734375
        x: 1.30078125
        x1: 0.802734375
        type: 'Q'
        y: -23.509765625
    ,
        y1: -23.24609375
        x: 2.296875
        x1: 1.798828125
        type: 'Q'
        y: -22.748046875
    ,
        y: -3.470703125
        x: 21.57421875
        type: 'L'
    ,
        y1: -3.236328125
        x: 21.8818359375
        x1: 21.779296875
        type: 'Q'
        y: -2.97265625
    ,
        y1: -2.708984375
        x: 21.8671875
        x1: 21.984375
        type: 'Q'
        y: -2.3427734375
    ,
        y1: -1.9765625
        x: 21.3544921875
        x1: 21.75
        type: 'Q'
        y: -1.44921875
    ,
        y1: -0.921875
        x: 20.197265625
        x1: 20.958984375
        type: 'Q'
        y: -0.130859375
    ,
        y1: 0.689453125
        x: 18.8203125
        x1: 19.376953125
        type: 'Q'
        y: 1.1142578125
    ,
        y1: 1.5390625
        x: 17.8681640625
        x1: 18.263671875
        type: 'Q'
        y: 1.685546875
    ,
        y1: 1.83203125
        x: 17.1943359375
        x1: 17.47265625
        type: 'Q'
        y: 1.7294921875
    ,
        y1: 1.626953125
        x: 16.681640625
        x1: 16.916015625
        type: 'Q'
        y: 1.392578125
    ,
        y1: -2.03515625
        x: 10.03125
        x1: 13.224609375
        type: 'Q'
        y: -5.4921875
    ,
        y1: -8.94921875
        x: 3.703125
        x1: 6.837890625
        type: 'Q'
        y: -12.40625
    ,
        y: 24.771484375
        x: 3.703125
        type: 'L'
    ,
        y1: 25.005859375
        x: 3.52734375
        x1: 3.703125
        type: 'Q'
        y: 25.2109375
    ,
        y1: 25.416015625
        x: 2.9560546875
        x1: 3.3515625
        type: 'Q'
        y: 25.5625
    ,
        y1: 25.708984375
        x: 1.8720703125
        x1: 2.560546875
        type: 'Q'
        y: 25.796875
    ,
        y1: 25.884765625
        x: 0.158203125
        x1: 1.18359375
        type: 'Q'
        y: 25.884765625
    ,
        y1: 25.884765625
        x: -1.5556640625
        x1: -0.8671875
        type: 'Q'
        y: 25.796875
    ,
        y1: 25.708984375
        x: -2.6396484375
        x1: -2.244140625
        type: 'Q'
        y: 25.5625
    ,
        y1: 25.416015625
        x: -3.2109375
        x1: -3.03515625
        type: 'Q'
        y: 25.2109375
    ,
        y1: 25.005859375
        x: -3.38671875
        x1: -3.38671875
        type: 'Q'
        y: 24.771484375
    ,
        y: -12.40625
        x: -3.38671875
        type: 'L'
    ,
        type: 'Z'
]


drawArrow = (ctx, scale) ->
    s = scale
    ctx.beginPath()
    i = 0
    while i < arrowCommands.length
        cmd = arrowCommands[i]
        if cmd.type == 'M'
            ctx.moveTo cmd.x * s, cmd.y * s
        else if cmd.type == 'L'
            ctx.lineTo cmd.x * s, cmd.y * s
        else if cmd.type == 'C'
            ctx.bezierCurveTo cmd.x1 * s, cmd.y1 * s, cmd.x2 * s, cmd.y2 * s, cmd.x * s, cmd.y * s
        else if cmd.type == 'Q'
            ctx.quadraticCurveTo cmd.x1 * s, cmd.y1 * s, cmd.x * s, cmd.y * s
        else if cmd.type == 'Z'
            ctx.closePath()
        i += 1


arrow = new Kinetic.Shape
    sceneFunc: (ctx) ->
        drawArrow ctx, 1.5
        ctx.fillStrokeShape this
    fill: cfg.arrowColor


smallArrow = new Kinetic.Shape
    sceneFunc: (ctx) ->
        drawArrow ctx, 0.75
        ctx.fillStrokeShape this
    fill: cfg.arrowColor
