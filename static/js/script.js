function toggleElementsState(elements, disabled) {
  Array.from(elements).forEach(function (el) {
    if (disabled) {
      el.setAttribute("disabled", true);
      el.disabled = true;
    } else {
      el.removeAttribute("disabled");
      el.disabled = false;
    }
  });
}

function addToMailingList(event) {
  event.preventDefault();

  var isTokensPage = window.location.pathname
    .split("/")
    .pop()
    .startsWith("ogn-token");

  var inputData = $(event.target).serialize();

  var formElements = event.target.querySelectorAll("input");
  toggleElementsState(formElements, true);

  $.post(
    "/mailing-list/join",
    inputData,
    function (data) {
      if (data.success && isTokensPage) {
        var presaleMailingList = document.getElementById(
          "presale-mailing-list"
        );
        presaleMailingList.classList.add("open");

        // var emailList = document.getElementById('add-to-mailing-list')
        // emailList.classList.remove('d-none')

        var emailInput = presaleMailingList.querySelector(
          "[type=email]",
          presaleMailingList
        );
        emailInput.value = decodeURIComponent(inputData.split("=").pop());
        emailInput.parentElement.classList.add("d-none");

      } else {
        toggleElementsState(formElements, false);
      }

      if (data.success) {
        if (window.onAddedToEmailList) {
          window.onAddedToEmailList()
        }
        fbq("track", "Lead");
      }

      alertify.log(data.message ? data.message : data, "default");
    },
    "json"
  );
}

function closeOgnOverlay(event) {
  event.preventDefault();
  $("#countdown-hero-banner").addClass("d-none").removeClass("d-flex")
}

$("#countdown-hero-banner-button").click(closeOgnOverlay);
$("#mailing-list").submit(addToMailingList);
$("#huobi-mail-list-1").submit(addToMailingList);
$("#huobi-mail-list-2").submit(addToMailingList);
$("#mailing-list-footer").submit(addToMailingList);
$("#mailing-list-nav-bar").submit(addToMailingList);

function presaleFormSubmit() {
  var emailList = document.getElementById("add-to-mailing-list");

  var presaleMailingList = document.getElementById("presale-mailing-list");
  var presaleForm = presaleMailingList.querySelector("form");
  var inputData = $(presaleForm).serialize();
  var formElements = presaleForm.querySelectorAll("input");
  toggleElementsState(formElements, true);
  $.post(
    "/presale/join",
    inputData,
    function (data) {
      if (data.success) {
        var presaleMailingList = document.getElementById(
          "presale-mailing-list"
        );
        if (presaleMailingList) {
          presaleMailingList.classList.remove("open");
        }

        fbq("track", "Lead");

        toggleElementsState(emailList.querySelectorAll("input"), false);
        emailList.querySelector("input[type=email]").value = "";
        window.scrollTo(0, 0);
      }

      toggleElementsState(formElements, false);
      alertify.log(data.message, "default");
    },
    "json"
  );
}

function partnerFormSubmit(event) {
  $.post(
    "/partners/interest",
    $("form").serialize(),
    function (data) {
      if (data == "OK") {
        fbq("track", "Lead");
        window.location = "/";
      }
      alertify.log(data, "default");
    },
    "json"
  );
}

$(function () {
  $(".dropdown-menu a").click(function () {
    $("input[name='desired_allocation_currency']").val($(this).text());
    $("#desired_allocation_currency").text($(this).text());
    $("#desired_allocation_currency").val($(this).text());
  });
});

// mobile navbar
$(function () {
  // toggle button icons
  $(".navbar-toggler").on("click", function () {
    var target = $(this);
    var other = $(".navbar-toggler").not(this);

    // attr value is a string, not bool
    if (target.attr("aria-expanded") === "false") {
      target.find(".close-icon").show();
      target.find(":not(.close-icon)").hide();
    } else {
      target.find(".close-icon").hide();
      target.find(":not(.close-icon)").show();
    }

    if (other.attr("aria-expanded") === "true") {
      other.find(".close-icon").hide();
      other.find(":not(.close-icon)").show();
    }
  });

  // prevent simulataneous navbar menus
  $(".navbar-origin .navbar-collapse").on("show.bs.collapse", function () {
    // ensure that menu is not hidden
    $(this).removeClass("obscured");
    // hide immediately to disguise 'hide' transition
    $(".navbar-origin .navbar-collapse")
      .not(this)
      .addClass("obscured");
    // will trigger transition
    $(".navbar-origin .navbar-collapse")
      .not(this)
      .collapse("hide");
  });

  // ensure that hidden menus can be shown
  $(".navbar-origin .navbar-collapse").on("hidden.bs.collapse", function () {
    $(".navbar-origin .navbar-collapse")
      .not(".show")
      .removeClass("obscured");
  });
});

// partners logos
$(function () {
  $(".collapse.logos").on("hidden.bs.collapse", function () {
    $(".more")
      .addClass("d-block")
      .removeClass("d-none");
    $(".less")
      .addClass("d-none")
      .removeClass("d-block");
  });

  $(".collapse.logos").on("shown.bs.collapse", function () {
    $(".more")
      .addClass("d-none")
      .removeClass("d-block");
    $(".less")
      .addClass("d-block")
      .removeClass("d-none");
  });
});

// show html content in tooltip
$('[data-toggle="tooltip"]').tooltip({
  html: true
});

// REDESIGN 2019 START
$(function () {
  function createElement(tag, props, children) {
    var namespace;

    if (tag === "svg" || tag === "circle") {
      namespace = "http://www.w3.org/2000/svg";
    }

    var element = namespace ?
      document.createElementNS(namespace, tag) :
      document.createElement(tag);

    var attributes = Object.keys(props);
    for (var i = 0; i < attributes.length; i++) {
      element.setAttribute(attributes[i], props[attributes[i]]);
    }

    if (children) {
      if (typeof children !== "object") {
        element.innerText = children;
      } else if (children.constructor === Array) {
        for (var i = 0; i < children.length; i++) {
          element.appendChild(children[i]);
        }
      } else {
        element.appendChild(children);
      }
    }

    return element;
  }

  function handleVideoResize(
    backgroundVideoElementId,
    videoAspectRatio,
    isVideoPlayer,
    bgPlayer,
    posterImageElement
  ) {
    var videoElement = document.getElementById(backgroundVideoElementId);
    var containerWidth = videoElement.parentElement.offsetWidth;
    var containerHeight = videoElement.parentElement.offsetHeight;

    if (containerHeight / videoAspectRatio > containerWidth) {
      var width = containerHeight / videoAspectRatio;
      var widthMargin = (width - containerWidth) / 2;
      if (isVideoPlayer) {
        if (bgPlayer) bgPlayer.setSize(width, containerHeight);
      } else {
        videoElement.style.width = width + "px";
        videoElement.style.height = containerHeight + "px";
      }

      if (posterImageElement) {
        posterImageElement.style.width = width + "px";
        posterImageElement.style.height = containerHeight + "px";
        posterImageElement.style.marginLeft = "-" + widthMargin + "px";
      }
    } else {
      var height = containerWidth * videoAspectRatio;
      if (isVideoPlayer) {
        if (bgPlayer) bgPlayer.setSize(containerWidth, height);
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
      width: "100%",
      height: "100%"
    };
    var isChineseLanguage = ["zh_Hant", "zh_Hans"].includes(
      document.body.parentElement.getAttribute("lang")
    );

    var fullScreenPlayerOpts = {};
    var currentLang = document.body.parentElement.getAttribute("lang");
    var currentVideoSource = videoSources[currentLang] ?
      videoSources[currentLang] :
      videoSources.default;

    var videoSource = currentVideoSource.videoSource;
    var backgroundVideoSource =
      currentVideoSource.alternateBackgroundSource || videoSource;
    videoSource = isChineseLanguage ?
      currentVideoSource.videoSourceYouku :
      videoSource;

    var aspectRatio = currentVideoSource.aspectRatio;
    var startTime = currentVideoSource.startTime || 0;
    var loopTime = currentVideoSource.loopTime || null;

    Object.assign(fullScreenPlayerOpts, playerOpts, {
      fullscreen: true,
      controls: true,
      playsInline: false
    });

    var backgroundElement = document.getElementById(backgroundElementId);
    if (!backgroundElement) {
      console.warn("Can not find element with id: ", backgroundElementId);
      return;
    }

    let videoPageVideoSource;
    let videoPageVideoSourceEn;
    if (!bgElementIsVideo) {
      const videoElement = $("#video-page-video");
      videoPageVideoSource = isChineseLanguage ?
        videoElement.attr("data-video-source-zh") :
        videoElement.attr("data-video-source");
      videoPageVideoSourceEn = videoElement.attr("data-video-source");
    }

    let posterImageHolder;
    let posterImage;
    // if poster image is used populate it and pass it to resize function
    if (videoPosterId) {
      posterImageHolder = document.getElementById(videoPosterId);
      posterRelativeHolder = createElement("div", {
        class: "video-overlay-poster-relative"
      });
      let posterImgSrc = videoPageVideoSourceEn;
      if (bgElementIsVideo) {
        posterImgSrc = currentVideoSource.posterImageOverride ?
          currentVideoSource.posterImageOverride :
          currentVideoSource.videoSource;
      }
      posterImgSrc = `/static/img/videos/${posterImgSrc}.jpg`;
      posterImage = createElement("img", {
        src: posterImgSrc
      });
      posterImageHolder.appendChild(posterRelativeHolder);
      posterRelativeHolder.appendChild(posterImage);
    }

    if (bgElementIsVideo && !isChineseLanguage) {
      var bgPlayer = new window.ytPlayer("#" + backgroundElementId, playerOpts);
      bgPlayer.load(backgroundVideoSource, true);
      bgPlayer.setVolume(0);
      bgPlayer.on("ended", () => {
        // loop
        bgPlayer.seek(startTime);
      });
      bgPlayer.on("timeupdate", seconds => {
        // jump to start time
        if (startTime && seconds < startTime) {
          bgPlayer.seek(startTime);
        }
        //early loop
        if (loopTime && seconds >= loopTime) {
          bgPlayer.seek(startTime);
        }

        // hide picture poster when video starts
        if (
          posterImageHolder &&
          ((startTime && seconds > startTime) || (!startTime && seconds > 0))
        ) {
          posterImageHolder.style.display = "none";
        }
      });
    }

    // video source is stored in data-video-source(-zh) property on video page
    if (!bgElementIsVideo) {
      videoSource = videoPageVideoSource;
    }

    var fullYoutubePlayer;
    var fullscreenYoukuPlayer;
    var exitFullScreenButton = document.getElementById(
      "exit-fullscreen-button"
    );

    if (!isChineseLanguage) {
      fullYoutubePlayer = new window.ytPlayer(
        "#" + fullScreenVideoElementId,
        fullScreenPlayerOpts
      );
    }

    //var isIOS = !!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform);

    function startFullScreenYoukuPlayer() {
      // youku video not yet available
      if (!videoSource || videoSource === "") {
        return false;
      }

      fullscreenYoukuPlayer = new YKU.Player(fullScreenVideoElementId, {
        client_id: "44503cca1be605b5",
        vid: videoSource,
        width: "100%",
        height: "100%",
        autoplay: true,
        show_related: false
      });

      // // show full screen button with slight delay
      setTimeout(function () {
        exitFullScreenButton.setAttribute("class", "");
      }, 3000);
      $(exitFullScreenButton).click(function () {
        closeFullScreen();
      });

      return true;
    }

    function stopFullScreenYoukuPlayer() {
      var fullScreenElement = document.getElementById(fullScreenVideoElementId);
      while (fullScreenElement.firstChild) {
        fullScreenElement.removeChild(fullScreenElement.firstChild);
      }
      exitFullScreenButton.setAttribute("class", "d-none");
    }

    if (fullYoutubePlayer) fullYoutubePlayer.load(videoSource);

    var socialLinks = document.querySelectorAll("[share-video-to]");

    for (var i = 0; i < socialLinks.length; i++) {
      var link = socialLinks[i];
      // we want to link people to the Origin site, not YouTube
      // var href = document.getElementById(fullScreenVideoElementId).getAttribute('src')
      var title = document.querySelector(".segment-title");
      switch (link.getAttribute("share-video-to")) {
        case "facebook":
          href =
            "http://www.facebook.com/sharer/sharer.php?u=" +
            encodeURIComponent(window.location.href);
          break;
        case "twitter":
          title = encodeURIComponent(title ? title.innerText + " " : "");
          href =
            "https://twitter.com/intent/tweet?text=" +
            title +
            encodeURIComponent(window.location.href);
          break;
        case "link":
          break;
      }

      link.setAttribute("href", href);
    }

    var isFullScreen = false;

    function closeFullScreen() {
      if (!isFullScreen) {
        return;
      }

      if (fullYoutubePlayer) {
        fullYoutubePlayer.stop();
      } else if (fullscreenYoukuPlayer) {
        stopFullScreenYoukuPlayer();
      }

      var el = document.getElementById(fullScreenVideoElementId);
      el.classList.add("d-none");
      el.onfullscreenchange = undefined;
      isFullScreen = false;
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.mozExitFullScreen) {
        document.mozExitFullScreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
    }

    function goFullscreen() {
      isFullScreen = true;
      // Youku embeded player does not support full screen on IOS
      if (fullscreenYoukuPlayer) {
        return;
      }

      var el = document.getElementById(fullScreenVideoElementId);

      var promise;
      if (el.requestFullscreen) {
        promise = el.requestFullscreen();
      } else if (el.mozRequestFullScreen) {
        promise = el.mozRequestFullScreen();
      } else if (el.webkitRequestFullscreen) {
        promise = el.webkitRequestFullscreen();
      } else if (el.msRequestFullscreen) {
        promise = el.msRequestFullscreen();
      } else {
        // on IOS none of the fullscreen functions are available, so we can
        // not detect when the user exits full screen. We just hide the inline
        // YouTube player and let the IOS native player take over and play the video
        setTimeout(() => {
          el.style.display = "none";
        }, 3000);
      }

      if (!promise) {
        return;
      }
      var flag = false;
      promise.then(function () {
        el.onfullscreenchange = function () {
          if (!flag) {
            // Hack to ignore the first fullscreen change event
            // We cannot differentiate fullscreen enter/exit otherwise
            flag = true;
            return;
          }
          closeFullScreen();
        };
      });
    }

    $(document).keyup(function (e) {
      if (e.key === "Escape") {
        closeFullScreen();
      }
    });

    // close the video when it ends
    if (fullYoutubePlayer) {
      fullYoutubePlayer.on("ended", () => {
        closeFullScreen();
      });
    }

    function callHandleVideoResize() {
      handleVideoResize(
        backgroundElementId,
        aspectRatio,
        bgElementIsVideo,
        bgPlayer,
        posterImage
      );
    }

    window.onresize = callHandleVideoResize;
    callHandleVideoResize();

    $("#" + videoButtonId).click(function () {
      if (fullYoutubePlayer) {
        fullYoutubePlayer.play();
      }
      // Chinese Youku player
      else {
        var youkuVideoConfigured = startFullScreenYoukuPlayer();
        if (!youkuVideoConfigured) return;
      }

      var el = document.getElementById(fullScreenVideoElementId);
      el.classList.remove("d-none");
      if (bgElementIsVideo && bgPlayer) {
        bgPlayer.seek(0);
      }

      goFullscreen();
    });
  }

  setupYoutubeVideoElement({
    backgroundElementId: "landing-video-background",
    videoSources: {
      default: {
        videoSource: "aanKtnkWP8U",
        videoSourceYouku: "XNDM5NzQ0NTEwMA",
        posterImageOverride: "aanKtnkWP8U_poster_image",
        alternateBackgroundSource: "GM8q0Cjzed4",
        aspectRatio: 0.42,
        loopTime: 69 // loop time in seconds
      }
      // Input other localisation videos this way
      // 'zh_Hans' : {
      //   videoSource: 'aanKtnkWP8U',
      //   videoSourceYouku: '',
      //   aspectRatio: 0.42,
      //   loopTime: 70
      // }
    },
    videoButtonId: "index-video-button",
    fullScreenVideoElementId: "landing-video",
    bgElementIsVideo: true,
    videoPosterId: "landing-video-poster"
  });

  setupYoutubeVideoElement({
    backgroundElementId: "landing-video-background2",
    videoSources: {
      default: {
        videoSource: "tAyusRT3ZDQ",
        videoSourceYouku: "XNDM4NjcxMjQwNA",
        alternateBackgroundSource: "hT4SlNP_iNY",
        posterImageOverride: "tAyusRT3ZDQ_poster_image",
        aspectRatio: 0.56,
        startTime: 72,
        loopTime: 120
      },
      ko: {
        videoSource: "GDDfAP150W8",
        videoSourceYouku: "XNDM4NjcxMjQwNA",
        alternateBackgroundSource: "hT4SlNP_iNY",
        aspectRatio: 0.56,
        startTime: 72,
        loopTime: 120
      },
      es: {
        videoSource: "OPobPJoYH7M",
        videoSourceYouku: "XNDM4NjcxMjQwNA",
        alternateBackgroundSource: "hT4SlNP_iNY",
        aspectRatio: 0.56,
        startTime: 72,
        loopTime: 120
      }
    },
    videoButtonId: "landing-video-button2",
    fullScreenVideoElementId: "landing-video2",
    bgElementIsVideo: true,
    videoPosterId: "landing-video-poster2"
  });

  setupYoutubeVideoElement({
    backgroundElementId: "about-video-background",
    videoSources: {
      default: {
        videoSource: "e70bvBw1oOo",
        videoSourceYouku: "",
        posterImageOverride: "e70bvBw1oOo_poster_image",
        aspectRatio: 0.56,
        startTime: 5
      }
    },
    videoButtonId: "about-video-button",
    fullScreenVideoElementId: "about-video",
    bgElementIsVideo: true,
    videoPosterId: "about-video-poster"
  });
  setupYoutubeVideoElement({
    backgroundElementId: "team-video-background",
    videoSources: {
      default: {
        videoSource: "ERh2n-vlpQ4",
        videoSourceYouku: "XNDM5NDQ3NjM1Mg",
        alternateBackgroundSource: "SlbKrVjOBjw",
        posterImageOverride: "5zsz1wUFmps_poster_image",
        aspectRatio: 0.56,
        startTime: 0
      }
    },
    videoButtonId: "team-video-button",
    fullScreenVideoElementId: "team-video",
    bgElementIsVideo: true,
    videoPosterId: "team-video-poster"
  });
  setupYoutubeVideoElement({
    backgroundElementId: "investors-video-background",
    videoSources: {
      default: {
        videoSource: "tAyusRT3ZDQ",
        videoSourceYouku: "XNDM4NjcxMjQwNA",
        posterImageOverride: "tAyusRT3ZDQ_poster_image",
        alternateBackgroundSource: "hT4SlNP_iNY",
        aspectRatio: 0.56,
        startTime: 72
      }
    },
    videoButtonId: "investors-video-button",
    fullScreenVideoElementId: "investors-video",
    bgElementIsVideo: true,
    videoPosterId: "investor-video-poster"
  });
  setupYoutubeVideoElement({
    backgroundElementId: "video-page-video-background",
    videoSources: {
      default: {
        videoSource: null,
        videoSourceYouku: null,
        aspectRatio: 0.56
      }
    },
    videoButtonId: "video-page-video-button",
    fullScreenVideoElementId: "video-page-video",
    bgElementIsVideo: false,
    videoPosterId: "videos-video-poster"
  });
});

$(function () {
  var socialSection = document.getElementById("social-media-list");
  var socialSectionRegionSpecific = document.getElementById(
    "social-media-list-country-specific"
  );

  if (!socialSection || !socialSectionRegionSpecific) return;

  var hardcodedStats = [{
      name: "Discord",
      subscribed_count: 4454
    },
    {
      name: "Wechat",
      subscribed_count: 5201
    },
    {
      name: "Vk",
      subscribed_count: 1780
    },
    {
      name: "Blockfolio",
      subscribed_count: 66294
    }
  ];

  var socialLegend = {
    Discord: {
      img: "/static/img/about/discord.svg",
      countLabel: "members",
      link: "https://discordapp.com/invite/jyxpUSe",
      regionSpecific: false
    },
    Telegram: {
      img: "/static/img/about/telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocol",
      regionSpecific: false
    },
    "Telegram (Korean)": {
      img: "/static/img/about/korean-telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocolkorea",
      regionSpecific: true
    },
    "Telegram (Vietnam)": {
      img: "/static/img/about/vietnam-telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocolvietnam",
      regionSpecific: true
    },
    "Telegram (Indonesia)": {
      img: "/static/img/about/indonesia-telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocolindonesia",
      regionSpecific: true
    },
    "Telegram (Russia)": {
      img: "/static/img/about/russia-telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocolrussia",
      regionSpecific: true
    },
    "Telegram (Spanish)": {
      img: "/static/img/about/spanish-telegram.svg",
      countLabel: "members",
      link: "https://t.me/originprotocolspanish",
      regionSpecific: true
    },
    Wechat: {
      img: "/static/img/about/china-wechat.svg",
      countLabel: "followers",
      qr: "/static/img/origin-wechat-qr.png",
      regionSpecific: true
    },
    Weibo: {
      img: "/static/img/about/weibo-china.svg",
      countLabel: "followers",
      qr: "/static/img/origin-weibo-qr.png",
      regionSpecific: true
    },
    Vk: {
      img: "/static/img/about/russia-vk.svg",
      countLabel: "subscribers",
      link: "https://vk.com/originprotocol",
      regionSpecific: true
    },
    Facebook: {
      img: "/static/img/about/facebook.svg",
      countLabel: "followers",
      link: "https://www.facebook.com/originprotocol",
      regionSpecific: false
    },
    Twitter: {
      img: "/static/img/about/twitter.svg",
      countLabel: "followers",
      link: "https://twitter.com/originprotocol",
      regionSpecific: false
    },
    Instagram: {
      img: "/static/img/about/instagram.svg",
      countLabel: "followers",
      link: "https://instagram.com/originprotocol",
      regionSpecific: false
    },
    Youtube: {
      img: "/static/img/about/youtube.svg",
      countLabel: "subscribers",
      link: "https://youtube.com/c/originprotocol",
      regionSpecific: false
    },
    Reddit: {
      img: "/static/img/about/reddit.svg",
      countLabel: "subscribers",
      link: "https://www.reddit.com/r/originprotocol",
      regionSpecific: false
    },
    Medium: {
      img: "/static/img/about/medium.svg",
      countLabel: "followers",
      link: "https://medium.com/originprotocol",
      regionSpecific: false
    },
    Blockfolio: {
      img: "/static/img/about/blockfolio.svg",
      countLabel: "followers",
      link: "https://blockfolio.com/coin/OGN",
      regionSpecific: false
    }
  };

  function createElementFromHTML(htmlString) {
    var div = document.createElement("div");
    div.innerHTML = htmlString.trim();
    return div.firstChild;
  }

  function intlFormat(num) {
    return new Intl.NumberFormat().format(Math.round(num * 10) / 10);
  }

  function formatNumber(num) {
    if (num >= 1000000) return intlFormat(num / 1000000) + "M";
    if (num >= 1000) return intlFormat(num / 1000) + "k";
    return intlFormat(num);
  }

  $.ajax({
    url: "/social-stats"
  }).done(function (data) {
    if (!data || !data.stats) return;

    data.stats = data.stats.concat(hardcodedStats);

    function renderStats(regionSpecific, appendToElement) {
      data.stats.forEach(stat => {
        var statMetadata = socialLegend[stat.name];

        if (!statMetadata || statMetadata.regionSpecific != regionSpecific)
          return;

        appendToElement.appendChild(
          createElementFromHTML(
            '<a class="d-flex flex-column social-box align-items-center" data-toggle="tooltip" target="_blank"' +
            (statMetadata.link ?
              'href="' + statMetadata.link + '"' :
              'href="#"') +
            (statMetadata.qr ?
              'data-container="body" data-original-title="<img src=\'' +
              statMetadata.qr +
              "' />\"" :
              ' title="' + stat.name + '"') +
            ">" +
            '<img src="' +
            statMetadata.img +
            '"/>' +
            '<div class="mt-auto">' +
            (stat.subscribed_count ?
              formatNumber(stat.subscribed_count) +
              " " +
              statMetadata.countLabel :
              "") +
            "</div>" +
            "</a>"
          )
        );
      });
    }

    renderStats(false, socialSection);
    renderStats(true, socialSectionRegionSpecific);

    // enable newly created tooltips
    $('[data-toggle="tooltip"]').tooltip({
      html: true
    });
  });
});

// To set defualt language
(function () {
  var langRegExp = /^\/[a-z]{2,3}(_[a-z]{4})?(\/|$)/i;
  if (!langRegExp.test(window.location.pathname)) {
    var currentLang = document.body.parentElement.getAttribute("lang");
    window.location = "/" + currentLang + window.location.pathname;
  }
})();