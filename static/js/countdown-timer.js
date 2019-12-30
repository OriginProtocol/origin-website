(function () {
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
      if (typeof children !== 'object') {
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

  function getDateDiff(date1, date2, omitDays) {
    var time1 = date1.getTime() / 1000
    var time2 = date2.getTime() / 1000

    var diff = time2 - time1

    if (diff <= 0) {
      return {
        seconds: '0',
        minutes: '0',
        hours: '0',
        days: '0',
        elapsed: true
      }
    }

    var seconds = Math.floor(diff % 60)
    var days = Math.floor(diff / (3600 * 24))
    var hours = Math.floor(diff / 3600) % 24
    var minutes = Math.floor(diff / 60) % 60

    if (omitDays) {
      return {
        seconds: String(seconds).padStart(2, '0'),
        minutes: String(minutes).padStart(2, '0'),
        hours: String(Math.floor(diff / 3600)).padStart(2, '0'),
      }
    } else {
      return {
        seconds: String(seconds).padStart(2, '0'),
        minutes: String(minutes).padStart(2, '0'),
        hours: String(hours).padStart(2, '0'),
        days: String(days).padStart(2, '0')
      }
    }
  }

  function getCompletionPercentage(startTime, endTime, now) {
    return 100 * ((now - startTime) / (endTime - startTime))
  }

  function buildTimeComponent(timeDiff, props) {
    const timeElements = [
      createElement('div', { class: 'time-group' }, [
        createElement('h1', { class: 'time-value' }, timeDiff.hours),
        createElement('div', { class: 'time-label' }, 'hours')
      ]),
      createElement('div', { class: 'colon' }, ':'),
      createElement('div', { class: 'time-group' }, [
        createElement('h1', { class: 'time-value' }, timeDiff.minutes),
        createElement('div', { class: 'time-label' }, 'minutes')
      ]),
      createElement('div', { class: 'colon' }, ':'),
      createElement('div', { class: 'time-group' }, [
        createElement('h1', { class: 'time-value' }, timeDiff.seconds),
        createElement('div', { class: 'time-label' }, 'seconds')
      ])
    ]

    if (!props.nav) {
      timeElements.unshift(createElement('div', { class: 'time-group' }, [
        createElement('h1', { class: 'time-value' }, timeDiff.days),
        createElement('div', { class: 'time-label' }, 'days')
      ]))
    }

    return createElement('div', {
      class: 'countdown-time-left'
    }, timeElements)
  }

  function CountdownTimer(element, props) {
    props = Object.assign({}, {
      large: false,
      startDate: new Date('08/31/2019'),
      placeholder: 'To be Announced',
      endDate: new Date('10/15/2019')
    }, props)

    console.log(props)
    var size = props.large ? 80 : 60
    var radius = size - 10
    var circumference = Math.PI * radius * 2

    var initialAngle = Math.ceil(circumference)
  
    if (!props.endDate) {
      var h1Element = createElement('h1', { class: 'time-group' }, props.placeholder);
      element.appendChild(h1Element);
      return;
    }

    var activeArc = createElement('circle', {
      r: radius,
      cx: size,
      cy: size,
      fill: 'transparent',
      class: 'active-arc',
      'stroke-dasharray': circumference,
      'stroke-dashoffset': 0
    })

    var bgArc = createElement('circle', {
      r: radius,
      cx: size,
      cy: size,
      fill: 'transparent',
      'stroke-dasharray': circumference
    })

    var svg = createElement('svg', {
      class: 'dial-svg',
      width: size * 2,
      height: size * 2,
      viewPort: '0 0 100 100',
      version: '1.1'
    }, [bgArc, activeArc])

    var dial = createElement('div', {
      class: 'dial d-flex'
    }, svg)
    
    element.classList.add('countdown-timer')
    if (props.nav) {
      element.classList.add('nav-timer')
    }
    props.large && element.classList.add('large')
    element.appendChild(dial)

    var now = new Date(Date.now())
    var diff = getDateDiff(now, props.endDate, props.nav)
    var timeComponent = buildTimeComponent(diff, props)

    element.appendChild(timeComponent)

    const intervalFunction = function () {
      var now = new Date(Date.now())

      var diff = getDateDiff(now, props.endDate, props.nav)

      if (diff.elapsed) {
        return clearInterval(interval)
      }

      element.removeChild(timeComponent)
      timeComponent = buildTimeComponent(diff, props)
      element.appendChild(timeComponent)

      var completed = getCompletionPercentage(props.startDate.getTime(), props.endDate.getTime(), now.getTime())
      // Min of 75%
      completed = 75 + (completed / 4)
      
      var completionAngle = ((100 - completed) / 100) * circumference

      activeArc.style.strokeDashoffset = completionAngle
    }

    activeArc.style.strokeDashoffset = initialAngle

    var interval = setInterval(intervalFunction, 1000)
  }

  function onDOMReady() {
    var timers = document.body.querySelectorAll('[data-countdown-timer]')

    for (var i = 0; i < timers.length; i++) {
      var timer = timers[i]

      if (timer.hasAttribute('data-timer-loaded')) {
        continue
      }
  
      new CountdownTimer(timer, {
        large: timer.hasAttribute('data-large'),
        nav: timer.hasAttribute('data-nav'),
        startDate: new Date(timer.getAttribute('data-startdate')),
        placeholder: timer.getAttribute('placeholder'),
        endDate: new Date(timer.getAttribute('data-enddate'))
      })

      timer.setAttribute('data-timer-loaded', true)
    }
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)

  window.CountdownTimer = CountdownTimer
})()
