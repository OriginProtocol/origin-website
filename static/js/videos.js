(function () {

  var tabHeaders = []
  var tabItems = []

  function setActiveTab(tabId) {
    tabHeaders.map(function (element) {
      if (tabId === element.getAttribute('data-category-group')) {
        element.classList.add('active')
      } else {
        element.classList.remove('active')
      }
    })

    tabItems.map(function (element) {
      if (tabId === element.getAttribute('data-category')) {
        element.classList.add('active')
      } else {
        element.classList.remove('active')
      }
    })
  }

  function onDOMReady() {
    tabHeaders = Array.from(
      document.querySelectorAll('[data-category-group]')
    )

    tabItems = Array.from(
      document.querySelectorAll('[data-category]')
    )

    var activeTab = tabHeaders.find(function (headerEl) {
      return headerEl.classList.contains('active')
    }) || tabHeaders[0]

    if (activeTab) {
      setActiveTab(activeTab.getAttribute('data-category-group'))
    }
  }

  function onDocClick(e) {
    if (!e.target.hasAttribute('data-category-group')) {
      return
    }

    e.preventDefault()

    setActiveTab(e.target.getAttribute('data-category-group'))
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
  document.addEventListener('click', onDocClick)
})()