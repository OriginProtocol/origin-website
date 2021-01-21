(function () {
  function onDOMReady() {

    var setupScrollListener = function () {
      var scrollImages = $('.parallax-scroll')
      var scrollImagesFaster = $('.parallax-scroll-faster')
      if (scrollImages.length === 0)
        return;

      var isMobileDevice = window.innerWidth <= 768
      
      var scrollFunction = function(e) {
        var setImageOffsets = function(images, isFast) {
          for (var i = 0; i < images.length; i++) {
            var image = images.get(i)
            var rect = image.getBoundingClientRect();
            var startOffset = isFast ? 0 : (isMobileDevice ? 40 : 20);
            var yOffset = isFast ? 0 : 40;
            var yScrollOffset = isFast ? 0 : 30;
            var scrollDelta = isMobileDevice ?
              (isFast ? 45 : 30) :
              (isFast ? 120 : 60);

            var inViewHeight = window.innerHeight + rect.height + scrollDelta;

            if (rect.y > -rect.height && rect.y < window.innerHeight + scrollDelta) {
              yOffset = yScrollOffset + (rect.y + rect.height) / inViewHeight * scrollDelta;
              image.style.top = `${yOffset + startOffset}px`;
            }
          }
        }
        setImageOffsets(scrollImages, false);
        setImageOffsets(scrollImagesFaster, true);
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

    var initTestimonialSlider = function(){
      $('#testimonial-slider').owlCarousel({
        loop:true,
        nav:false,
        responsive:{
            0:{
                items:1
            },
            1000:{
                items:2
            }
        }
    })
    }

    setupMobileMenu();
    setupScrollListener();
    initTestimonialSlider()
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
})()
