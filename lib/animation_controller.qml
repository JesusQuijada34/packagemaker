import QtQuick 2.15

QtObject {
    id: controller

    signal animateRequested(var target, string propertyName, var startValue,
                            var endValue, int duration, string easingName,
                            int animationId)
    signal cancelRequested(int animationId)
    signal animationFinished(int animationId)
    property var activeAnimations: ({})

    function easingValue(name) {
        switch (name) {
        case "outExpo": return Easing.OutExpo
        case "outBounce": return Easing.OutBounce
        case "inOutCubic": return Easing.InOutCubic
        case "linear": return Easing.Linear
        default: return Easing.OutCubic
        }
    }

    function cancelAnimation(animationId) {
        const animation = activeAnimations[animationId]
        if (animation) {
            animation.stop()
            delete activeAnimations[animationId]
            animation.destroy()
        }
    }

    onAnimateRequested: function(target, propertyName, startValue, endValue,
                                 duration, easingName, animationId) {
        cancelAnimation(animationId)
        const animation = Qt.createQmlObject(
            "import QtQuick 2.15; PropertyAnimation { }",
            controller,
            "centralPropertyAnimation"
        )
        animation.target = target
        animation.property = propertyName
        animation.from = startValue
        animation.to = endValue
        animation.duration = duration
        animation.easing.type = easingValue(easingName)
        activeAnimations[animationId] = animation
        animation.finished.connect(function() {
            delete activeAnimations[animationId]
            animationFinished(animationId)
            animation.destroy()
        })
        animation.start()
    }

    onCancelRequested: function(animationId) {
        cancelAnimation(animationId)
    }
}
