(function () {
  function onDOMReady() {
    var scrollImages = $('.parallax-scroll')
    if (scrollImages.length === 0)
      return;

    window.addEventListener('scroll', function(e) {
      for (var i = 0; i < scrollImages.length; i++) {
        var image = scrollImages.get(i)
        var rect = image.getBoundingClientRect();
        var yOffset = 40;
        var scrollDelta = 80;
        var inViewHeight = window.innerHeight + rect.height + scrollDelta;

        if (rect.y > -rect.height && rect.y < window.innerHeight + scrollDelta) {
          yOffset = (rect.y + rect.height) / inViewHeight * scrollDelta;
          image.style.top = `${yOffset + 20}px`;
        }
      }
    })
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
})()
