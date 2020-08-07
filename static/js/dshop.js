(function () {
  function onDOMReady() {

    var setupScrollListener = function () {
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
      
      scrollFunction();
      window.addEventListener('scroll', scrollFunction);
    }

    var setupMobileMenu = function () {
      var menuButton = document.getElementById("dshop-menu-button");
      var closeButton = document.getElementById("dshop-close-button");
      var background = document.getElementById("dshop-background");

      if (!menuButton || !closeButton) {
        return 
      }

      menuButton.onclick = function(e) {
        e.preventDefault()
        document.getElementById("dshop-sidenav").style.width = "256px";
        background.style.background = "rgba(0, 0, 0, 0.4)";
        background.style.visibility = "visible";
      }

      var closeNav = function(e) {
        document.getElementById("dshop-sidenav").style.width = "0px";
        background.style.background = "rgba(0, 0, 0, 0)";
        background.style.visibility = "hidden";
      }

      $(".dshop-sidenav .nav-item").click(closeNav);
      closeButton.onclick = closeNav;
      background.onclick = closeNav;
    }

    setupMobileMenu();
    setupScrollListener();
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
})()
