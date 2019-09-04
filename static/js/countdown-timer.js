(() => {
  function createElement(tag, props, children) {
    var namespace

    if (tag === 'svg' || tag === 'circle') {
      namespace = 'http://www.w3.org/2000/svg'
    }

    var element = namespace ? document.createElementNS(namespace, tag) : document.createElement(tag)

    var attributes = Object.keys(props)
    for (var i = 0; i < attributes.length; i++) {
      element.setAttribute(attributes[i], props[attributes[i]])
    }

    if (children) {
      if (typeof children === 'string') {
        element.innerText = children
      } else if (children.constructor === Array) {
        for (var i = 0; i < children.length; i++) {
          element.appendChild(children[i])
        }
      } else {
        element.appendChild(children)
      }
    }

    return element
  }

  function getDateDiff(date1, date2) {
    var time1 = date1.getTime()
    var time2 = date2.getTime()

    return {
      seconds: 12,
      minutes: 43,
      hours: 23,
      days: 30,
      elapsed: false
    }
  }

  function getCompletionPercentage(startTime, endTime, now) {
    return 100 * ((now - startTime) / (endTime - startTime))
  }

  function CountdownTimer(element, props) {
    props = Object.assign({}, {
      large: false,
      startDate: new Date('08/31/2019'),
      endDate: new Date('10/15/2019')
    }, props)

    var size = props.large ? 100 : 100
    var radius = size - 10
    var circumference = Math.PI * radius * 2

    var activeArc = createElement('circle', {
      r: radius,
      cx: size,
      cy: size,
      fill: 'transparent',
      class: 'active-arc',
      'stroke-dasharray': 565.48,
      'stroke-dashoffset': 0
    })

    var bgArc = createElement('circle', {
      r: radius,
      cx: size,
      cy: size,
      fill: 'transparent',
      'stroke-dasharray': 565.48,
      'stroke-dashoffset': 0
    })

    var svg = createElement('svg', {
      class: 'dial-svg',
      width: 200,
      height: 200,
      viewPort: '0 0 100 100',
      version: '1.1'
    }, [bgArc, activeArc])

    var dial = createElement('div', {
      class: 'dial'
    }, svg)
    
    element.classList.add('countdown-timer')
    element.appendChild(dial)

    var interval = setInterval(function () {
      var now = new Date(Date.now())

      var diff = getDateDiff(now, props.endDate)

      if (diff.elapsed) {
        return clearInterval(interval)
      }

      var completed = getCompletionPercentage(props.startDate.getTime(), props.endDate.getTime(), now.getTime())
      // Min of 75%
      completed = 75 + (completed / 4)
      
      var completionAngle = ((100 - completed) / 100) * circumference

      activeArc.style.strokeDashoffset = completionAngle
    }, 1000)
  }

  window.CountdownTimer = CountdownTimer
})()