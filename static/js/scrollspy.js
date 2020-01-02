$(function() {
  const container = document.getElementById('whitepaperNavbar')

  if (!container) {
    return
  }

  const links = Array.from(document.querySelectorAll('#whitepaperNavbar a'))
  const containerEls = links.map(link => document.querySelector(link.getAttribute('href')))

  const onScroll = () => {

    for (let i = 0; i < links.length; i++) {
      const link = links[i]

      const element = containerEls[i]
      const rect = element.getBoundingClientRect()

      const hasScrolledPast = -rect.y > rect.height

      const isActive = rect.y < 150

      if (!hasScrolledPast && isActive) {
        link.classList.add('active')
      } else {
        link.classList.remove('active')
      }
    }
  }

  window.onscroll = onScroll
})