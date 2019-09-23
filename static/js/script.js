function submitEmailForm (event) {
  $.post('/mailing-list/join', $(event.target).serialize(), function(data) {
      $("#signup-result").html(data);
      alertify.log(data, "default");
      fbq('track', 'Lead');
    },
    'json'
  );
  event.preventDefault();
}

$("#mailing-list").submit(submitEmailForm);
$("#mailing-list-footer").submit(submitEmailForm);

function presaleFormSubmit(event) {
  $.post('/presale/join', $('form').serialize(), function(data) {
    if (data == "OK") {
      fbq('track', 'Lead');
      window.location = "/";
    }
    alertify.log(data, "default");
  },
  'json')
}

function partnerFormSubmit(event) {
  $.post('/partners/interest', $('form').serialize(), function(data) {

    if (data == "OK") {
      fbq('track', 'Lead');
      window.location = "/";
    }
    alertify.log(data, "default");
  },
  'json');
}


$(function() {
  $(".dropdown-menu a").click(function() {
    $("input[name='desired_allocation_currency']").val($(this).text());
    $("#desired_allocation_currency").text($(this).text());
    $("#desired_allocation_currency").val($(this).text());
  });
});

// mobile navbar
$(function(){
  // toggle button icons
  $('.navbar-toggler').on('click', function() {
    var target = $(this);
    var other = $('.navbar-toggler').not(this);

    // attr value is a string, not bool
    if (target.attr('aria-expanded') === 'false') {
      target.find('.close-icon').show();
      target.find(':not(.close-icon)').hide();
    } else {
      target.find('.close-icon').hide();
      target.find(':not(.close-icon)').show();
    }

    if (other.attr('aria-expanded') === 'true') {
      other.find('.close-icon').hide();
      other.find(':not(.close-icon)').show();
    }
  });

  // prevent simulataneous navbar menus
  $('.navbar-origin .navbar-collapse').on('show.bs.collapse', function() {
    // ensure that menu is not hidden
    $(this).removeClass('obscured');
    // hide immediately to disguise 'hide' transition
    $('.navbar-origin .navbar-collapse').not(this).addClass('obscured');
    // will trigger transition
    $('.navbar-origin .navbar-collapse').not(this).collapse('hide');
  });

  // ensure that hidden menus can be shown
  $('.navbar-origin .navbar-collapse').on('hidden.bs.collapse', function() {
    $('.navbar-origin .navbar-collapse').not('.show').removeClass('obscured');
  });
});

// partners logos
$(function() {
  $('.collapse.logos').on('hidden.bs.collapse', function() {
    $('.more').addClass('d-block').removeClass('d-none');
    $('.less').addClass('d-none').removeClass('d-block');
  });

  $('.collapse.logos').on('shown.bs.collapse', function() {
    $('.more').addClass('d-none').removeClass('d-block');
    $('.less').addClass('d-block').removeClass('d-none');
  });
});

// show html content in tooltip
$('[data-toggle="tooltip"]').tooltip({
  html: true
});

// REDESIGN 2019 START
$(function() {
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

  function handleVideoResize(backgroundVideoElementId, videoAspectRatio, isVideoPlayer, bgPlayer, posterImageElement) {
    var videoElement = document.getElementById(backgroundVideoElementId)
    var containerWidth = videoElement.parentElement.offsetWidth;
    var containerHeight = videoElement.parentElement.offsetHeight;

    if (containerHeight / videoAspectRatio > containerWidth) {
      var width = containerHeight/videoAspectRatio;
      if (isVideoPlayer){
        bgPlayer.setSize(width, containerHeight);
      } else {
        videoElement.style.width = width + "px";
        videoElement.style.height = containerHeight + "px";
      }

      if (posterImageElement) {
        posterImageElement.style.width = width + "px";
        posterImageElement.style.height = containerHeight + "px"; 
      }
    } else {
      var height = containerWidth*videoAspectRatio;
      if (isVideoPlayer) {
        bgPlayer.setSize(containerWidth, height);
      } else {
        videoElement.style.width = containerWidth + "px";
        videoElement.style.height = height + "px";
      }

      if (posterImageElement) {
        posterImageElement.style.width = containerWidth + "px";
        posterImageElement.style.height = height + "px";
      }
    }
  }

  function setupYoutubeVideoElement({
    backgroundElementId,
    videoSources,
    videoButtonId,
    fullScreenVideoElementId,
    bgElementIsVideo,
    videoPosterId
  }) {
    var playerOpts = {
      autoplay: true,
      controls: false,
      fullscreen: false,
      related: false,
      info: false,
      related: false,
      width: '100%',
      height: '100%'
    };

    var fullScreenPlayerOpts = {};
    var currentLang = document.body.parentElement.getAttribute('lang')
    var currentVideoSource = videoSources[currentLang] ? videoSources[currentLang] : videoSources.default


    var videoSource = currentVideoSource.videoSource
    var aspectRatio = currentVideoSource.aspectRatio
    var startTime = currentVideoSource.startTime || 0
    var loopTime = currentVideoSource.loopTime || null

    Object.assign(fullScreenPlayerOpts, playerOpts, {
      fullscreen: true,
      controls: true,
      playsInline: false
    });

    var backgroundElement = document.getElementById(backgroundElementId);
    if (!backgroundElement) {
      console.warn('Can not find element with id: ', backgroundElementId);
      return;
    }

    let posterImageElement
    // if poster image is used populate it and pass it to resize function
    if (videoPosterId) {
      posterImageElement = document.getElementById(videoPosterId)
      posterImageElement.appendChild(createElement('img', { src: `/static/img/videos/${videoSource}_poster_image.png` }))
    }

    if (bgElementIsVideo) {
      var bgPlayer = new window.ytPlayer('#' + backgroundElementId, playerOpts);
      bgPlayer.load(videoSource, true);
      bgPlayer.setVolume(0);
      bgPlayer.on('ended', () => {
        // loop
        bgPlayer.seek(startTime);
      });
      bgPlayer.on('timeupdate', (seconds) => {
        // jump to start time
        if (startTime && seconds < startTime) {
          bgPlayer.seek(startTime);
        }
        //early loop
        if (loopTime && seconds >= loopTime) {
          bgPlayer.seek(startTime);
        }

        // hide picture poster when video starts
        if (posterImageElement &&
          (
            (startTime && seconds > startTime) ||
            (!startTime && seconds > 0)
          )
        ) {
          posterImageElement.style.display = 'none';
        }
      });
    }
      
    // video source is stored in data-video-source property
    if (!bgElementIsVideo) {
      videoSource = $('#video-page-video').attr("data-video-source");
    }

    var fullPlayer = new window.ytPlayer('#' + fullScreenVideoElementId, fullScreenPlayerOpts);
    fullPlayer.load(videoSource);

    fullPlayer.on('unstarted', function () {
      var socialLinks = document.querySelectorAll('[share-video-to]')
  
      for (var i = 0; i < socialLinks.length; i++) {
        var link = socialLinks[i]
        var href = document.getElementById(fullScreenVideoElementId).getAttribute('src')
        var title = document.querySelector('.segment-title')
        switch (link.getAttribute('share-video-to')) {
          case 'facebook':
            href = 'http://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(href)
            break
          case 'twitter':
            title = encodeURIComponent(title ? title.innerText + ' ' : '')
            href = 'https://twitter.com/intent/tweet?text=' + title + encodeURIComponent(href)
            break
        }

        link.setAttribute('href', href)
      }
    })

    function closeFullScreen() {
      fullPlayer.stop();
      var el = document.getElementById(fullScreenVideoElementId)
      el.classList.add('d-none')
      el.onfullscreenchange = undefined
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if (document.mozExitFullScreen) {
        document.mozExitFullScreen()
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen()
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen()
      }
    }  

    function goFullscreen() {
      var el = document.getElementById(fullScreenVideoElementId)

      var promise
      if (el.requestFullscreen) {
        promise = el.requestFullscreen()
      } else if (el.mozRequestFullScreen) {
        promise = el.mozRequestFullScreen()
      } else if (el.webkitRequestFullscreen) {
        promise = el.webkitRequestFullscreen()
      } else if (el.msRequestFullscreen) {
        promise = el.msRequestFullscreen()
      }

      if (!promise) {
        return
      }
      var flag = false
      promise
        .then(function () {
          el.onfullscreenchange = function () {
            if (!flag) {
              // Hack to ignore the first fullscreen change event
              // We cannot differentiate fullscreen enter/exit otherwise
              flag = true
              return
            }
            closeFullScreen()
          }
        })
    }

    $(document).keyup(function(e) {
      if (e.key === "Escape") {
        closeFullScreen()
      }
    });

    // close the video when it ends
    fullPlayer.on('ended', () => {
      closeFullScreen()
    });

    function callHandleVideoResize() {
      handleVideoResize(backgroundElementId, aspectRatio, bgElementIsVideo, bgPlayer, posterImageElement);
    }

    window.onresize = callHandleVideoResize;
    callHandleVideoResize();

    $('#' + videoButtonId).click(function() {
      var el = document.getElementById(fullScreenVideoElementId)
      el.classList.remove('d-none')
      if (bgElementIsVideo) {
        bgPlayer.seek(0);
      }

      goFullscreen()
      fullPlayer.play();
    });
  }

  setupYoutubeVideoElement({
    backgroundElementId: 'landing-video-background',
    videoSources: {
      'default': {
        videoSource: 'aanKtnkWP8U',
        aspectRatio: 0.42,
        loopTime: 70, // loop time in seconds
      },
      // Input other localisation videos this way 
      // 'zh_Hans' : {
      //   videoSource: 'aanKtnkWP8U',
      //   aspectRatio: 0.42,
      //   loopTime: 70
      // }
    },
    videoButtonId: 'index-video-button',
    fullScreenVideoElementId: 'landing-video',
    bgElementIsVideo: true,
    videoPosterId: 'landing-video-poster'
  })

  setupYoutubeVideoElement({
    backgroundElementId: 'landing-video-background2',
    videoSources: {
      'default': {
        videoSource: 'tAyusRT3ZDQ',
        aspectRatio: 0.56,
        startTime: 72
      }
    },
    videoButtonId: 'landing-video-button2',
    fullScreenVideoElementId: 'landing-video2',
    bgElementIsVideo: true,
    videoPosterId: 'landing-video-poster2'
  })

  setupYoutubeVideoElement({
    backgroundElementId: 'about-video-background',
    videoSources: {
      'default': {
        videoSource: 'e70bvBw1oOo',
        aspectRatio: 0.56,
        startTime: 5
      }
    },
    videoButtonId: 'about-video-button',
    fullScreenVideoElementId: 'about-video',
    bgElementIsVideo: true,
    videoPosterId: 'about-video-poster'
  })
  setupYoutubeVideoElement({
    backgroundElementId: 'team-video-background',
    videoSources: {
      'default': {
        videoSource: 'ERh2n-vlpQ4',
        aspectRatio: 0.56,
        startTime: 15
      }
    },
    videoButtonId: 'team-video-button',
    fullScreenVideoElementId: 'team-video',
    bgElementIsVideo: true,
    videoPosterId: 'team-video-poster'
  })
  setupYoutubeVideoElement({
    backgroundElementId: 'investors-video-background',
    videoSources: {
      'default': {
        videoSource: 'tAyusRT3ZDQ',
        aspectRatio: 0.56,
        startTime: 72
      }
    },
    videoSource: 'tAyusRT3ZDQ',
    videoButtonId: 'investors-video-button',
    fullScreenVideoElementId: 'investors-video',
    bgElementIsVideo: true,
    videoPosterId: 'investor-video-poster'
  })
  setupYoutubeVideoElement({
    backgroundElementId: 'video-page-video-background',
    videoSources: {
      'default': {
        videoSource: null,
        aspectRatio: 0.56
      }
    },
    videoButtonId: 'video-page-video-button',
    fullScreenVideoElementId: 'video-page-video',
    bgElementIsVideo: false
  })
});

$(function() {
  var socialSection = document.getElementById('social-media-list')
  if (!socialSection)
    return

  var socialLegend = {
    'Discord': {
      'img': '/static/img/about/discord.svg',
      'countLabel': 'members',
      'link': 'https://discordapp.com/invite/jyxpUSe'
    },
    'Telegram': {
      'img': '/static/img/about/telegram.svg',
      'countLabel': 'members',
      'link': 'https://t.me/originprotocol'
    },
    'Telegram (Korean)': {
      'img': '/static/img/about/telegram.svg',
      'countLabel': 'members',
      'link': 'https://t.me/OriginProtocolKorea'
    },
    'Wechat': {
      'img': '/static/img/about/wechat.svg',
      'countLabel': 'followers',
      'qr': '/static/img/origin-wechat-qr.png'
    },
    'KaKao plus friends': {
      'img': '/static/img/about/kakao.svg',
      'countLabel': 'subscribers',
      'qr': '/static/img/origin-kakao-qr.png'
    },
    'Facebook': {
      'img': '/static/img/about/facebook.svg',
      'countLabel': 'followers',
      'link': 'https://www.facebook.com/originprotocol'
    },
    'Twitter': {
      'img': '/static/img/about/twitter.svg',
      'countLabel': 'followers',
      'link': 'https://twitter.com/originprotocol'
    },
    'Instagram': {
      'img': '/static/img/about/instagram.svg',
      'countLabel': 'followers',
      'link': 'https://instagram.com/originprotocol'
    },
    'Youtube': {
      'img': '/static/img/about/youtube.svg',
      'countLabel': 'subscribers',
      'link': 'https://youtube.com/c/originprotocol'
    },
    'Reddit': {
      'img': '/static/img/about/reddit.svg',
      'countLabel': 'subscribers',
      'link': 'https://www.reddit.com/r/'
    },
    'Medium': {
      'img': '/static/img/about/medium.svg',
      'countLabel': 'followers',
      'link': 'https://medium.com/originprotocol'
    }
  }

  function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild; 
  }

  function intlFormat(num)
  {
    return new Intl.NumberFormat().format(Math.round(num*10)/10);
  }

  function formatNumber(num)
  {
    if(num >= 1000000)
      return intlFormat(num/1000000)+'M';
    if(num >= 1000)
      return intlFormat(num/1000)+'k';
    return intlFormat(num);
  }


  $.ajax({
    url: '/social-stats'
  })
    .done(function( data ) {
      if (!data || !data.stats)
        return

      data.stats.forEach(stat => {
        var statMetadata = socialLegend[stat.name]
        if(!statMetadata)
          return

        socialSection.appendChild(createElementFromHTML(
          '<a class="d-flex flex-column social-box align-items-center"' + 
            (statMetadata.link ? ('href="' + statMetadata.link + '"') : 'href="#"') + 
            (statMetadata.qr ? 'data-container="body" data-toggle="tooltip" title="" data-original-title="<img src=\'' + statMetadata.qr + '\' />"' : '') +
          '>' +
              '<img src="' + statMetadata.img + '"/>' +
              '<div class="mt-auto">' + formatNumber(stat.subscribed_count) + ' ' + statMetadata.countLabel  + '</div>' +
          '</a>'
        ))
      })

      // enable newly created tooltips
      $('[data-toggle="tooltip"]').tooltip({
        html: true
      });

    })
});

// To set defualt language
(function() {
  var langRegExp = /^\/[a-z]{2,3}(_[a-z]{4})?(\/|$)/i
  if(!langRegExp.test(window.location.pathname)) {
    var currentLang = document.body.parentElement.getAttribute('lang')
    window.location = '/' + currentLang + window.location.pathname
  }
})()
