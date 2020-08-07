(function () {
  function onDOMReady() {
    var scrollImages = $('.parallax-scroll')
    if (scrollImages.length === 0)
      return;

    var isMobileDevice = window.innerWidth <= 768

    var scrollFunction = function(e) {
      for (var i = 0; i < scrollImages.length; i++) {
        var image = scrollImages.get(i)
        var rect = image.getBoundingClientRect();
        var startOffset = isMobileDevice ? 40 : 20;
        var yOffset = 40;
        var scrollDelta = isMobileDevice ? 30 : 80;

        var inViewHeight = window.innerHeight + rect.height + scrollDelta;

        if (rect.y > -rect.height && rect.y < window.innerHeight + scrollDelta) {
          yOffset = (rect.y + rect.height) / inViewHeight * scrollDelta;
          image.style.top = `${yOffset + startOffset}px`;
        }
      }
    }
    
    scrollFunction()
    window.addEventListener('scroll', scrollFunction)
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
})()
