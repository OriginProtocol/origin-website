var YK = {};
YK.https = location.protocol;
window.YKU = {};
var YKP = {
  playerType: "",
  playerState: {
    PLAYER_STATE_INIT: 'PLAYER_STATE_INIT',
    PLAYER_STATE_READY: 'PLAYER_STATE_READY',
    PLAYER_STATE_AD: 'PLAYER_STATE_AD',
    PLAYER_STATE_PLAYING: 'PLAYER_STATE_PLAYING',
    PLAYER_STATE_END: 'PLAYER_STATE_END',
    PLAYER_STATE_ERROR: 'PLAYER_STATE_ERROR'
  },

  playerCurrentState: 'PLAYER_STATE_INIT',
  isLoadFinishH5: false,
  isPC: true,
  videoList: [],
  isAndroidYouku: false
};

var StaticDomain = YK.https + "//player.youku.com";

function browserRedirect() {
  var sUserAgent = navigator.userAgent.toLowerCase();
  var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
  var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
  var bIsIphone = sUserAgent.match(/iphone/i) == "iphone";
  var bIsMidp = sUserAgent.match(/midp/i) == "midp";
  var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
  var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb";
  var bIsAndroid = sUserAgent.match(/android/i) == "android";
  var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
  var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";
  if (bIsIpad || bIsIphoneOs || bIsIphone || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
    YKP.isPC = false;
    //YKP.isSupportFlash = false;
  } else {
    YKP.isPC = true;
    //YKP.isSupportFlash = true;
  }
  var bIsYouku = sUserAgent.match(/youku/i) == "youku";
  if (bIsAndroid) {
    if (bIsYouku) {
      YKP.isAndroidYouku = true;
    }
  }

  if (bIsIphone) {
    if (bIsYouku) {
      YKP.isIphoneYouku = true;
    }
  }
}
browserRedirect();

function createIFrame(w, h, parentName, vid, partnerId, password, autoplay, events) {
  if (YKP.isPC) {
    var iframes = document.getElementById(parentName + '').getElementsByTagName("iframe");

    while (iframes.length) {
      var parentElement = iframes[0].parentNode;
      if (parentElement) {
        parentElement.removeChild(iframes[0])
      }
    }

    var iframe = document.createElement('iframe');
    iframe.setAttribute('width', w);
    iframe.setAttribute('height', h);
    iframe.setAttribute('allow', 'autoplay');
    var srcUrl = StaticDomain + '/embed/' + vid + '?client_id=' + partnerId + '&password=' + password + '&autoplay=' + autoplay+ '#' + window.location.host;

    if (events && events.onPlayStart) {
      srcUrl += '&onPlayStart=' + events.onPlayStart;
    }

    if (events && events.onPlayEnd) {
      srcUrl += '&onPlayEnd=' + events.onPlayEnd;
    }
    iframe.setAttribute('src', srcUrl);
    iframe.setAttribute('name','iframeId');
    iframe.setAttribute('id', 'iframeId');
    iframe.setAttribute('frameborder', 0);
    iframe.setAttribute('allowfullscreen', true);
    iframe.setAttribute('scrolling', 'no');
    document.getElementById(parentName + '').appendChild(iframe);
    return iframe;
  }
  return null;
}

var urlParameter = function(object) {
  var arr = [];
  for (var o in object) {
    arr.push(o + '=' + object[o]);
  }
  return arr.join('&');
};

window.QS = function() {
  var args = {};
  var result = window.location.search.match(new RegExp("[\?\&][^\?\&]+=[^\?\&]+", "g"));
  if (result != null) {
    for (var i = 0; i < result.length; i++) {
      var ele = result[i];
      var inx = ele.indexOf("=");
      //args[ele.substring(1, inx)] = ele.substring(inx + 1);
      var key = ele.substring(1, inx);
      var val = ele.substring(inx + 1);
      try {
        val = decodeURI(val);
      } catch (e) {

      }
      //Ã¨Â½Â¬Ã¦ÂÂ¢val Boolean Number Object
      val == "true" ? val = true : (val == "false" ? val == false : isNaN(val) ? val = parseJsonStr(val) : val = +val);
      if ('undefined' == typeof args[key]) {
        args[key] = val;
      } else {
        if (args[key] instanceof Array) {
          args[key].push(val);
        } else {
          args[key] = [args[key], val];
        }
      }
    }
  }
  return args;
}

function parseJsonStr(str) {
  if ('string' != typeof str) {
    return str;
  }
  if (/{[^{^}]{0,}}/.test(str)) {
    try {
      str = JSON.parse(str);
    } catch (e) {

    }
  }
  return str;
}

var dynamicLoading = {
  css: function(path) {
    if (!path || path.length === 0) {
      throw new Error('argument "path" is required !');
    }
    var head = document.getElementsByTagName('head')[0];
    var link = document.createElement('link');
    link.href = path;
    link.rel = 'stylesheet';
    link.type = 'text/css';
    head.appendChild(link);
  },
  js: function(path, obj, attr) {
    if (!path || path.length === 0) {
      throw new Error('argument "path" is required !');
    }
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.src = path;
    script.type = 'text/javascript';
    if (attr) {
      script["id"] = attr["id"];
      script.setAttribute('pageType', attr["pageType"]);
      script.setAttribute('isHidden', attr["isHidden"]);
    }
    head.appendChild(script);

    script.onload = function() {
      if (obj) {
        obj.selectH5();
        YKP.isLoadFinishH5 = true;
      }
    }
  }
}

dynamicLoading.css(YK.https + "//player.youku.com/unifull/css/unifull.min.css?v=20190124");

var YoukuPlayerSelect = function(params) {

  YK.initConfig = params;
  this._vid = params.vid;
  this._target = params.target;
  this._partnerId = params.partnerId;
  this._videoFlag = params.videoFlag;
  if (params.client_id) {
    //å…¼å®¹openapiä¸­çš„client_idçš„è®¾ç½®
    this._partnerId = params.client_id;
  }

  if (!(this._vid && this._target && this._partnerId)) {
    alert(
      "[Fail]The params of {vid,target,client_id} are necessary !"
    );
    return;
  }

  this._events = params.events;
  YK.playerEvents = params.events;

  this._id = params.id;
  if (this._id == null) this._id = "youku-player";
  YKP.playerId = this._id;
  this._width = params.width;
  this._height = params.height;
  this._expand = params.expand;
  if (params.width == null || params.height == null) {
    //å®½é«˜æŒ‡å®šä¸å…¨ï¼Œé»˜è®¤ä¸º0
    if (params.expand == null) {
      this._expand = 0;
    }
  } else {
    //å®½é«˜éƒ½æŒ‡å®šï¼Œé»˜è®¤ä¸º1
    if (params.expand == null) {
      this._expand = 1;
    }
  }

  // this._prefer = (params.prefer ? params.prefer.toLowerCase() : "flash");
  this._starttime = params.starttime;
  this._password = params.password ? params.password : '';
  this._poster = params.poster;
  this._autoplay = !!params.autoplay; // 0 ,1 ,true ,false,'true','false'..
  this._canWide = params.canWide;
  if ('undefined' != typeof params.show_related) {
    this._showRelated = !!params.show_related;
  }

  this._embed_content = params.embed_content;
  this._embed_vid = params.embed_vid;
  this._cancelFullScreen = params.cancelFullScreen;
  this._titleStyle = params.titleStyle;
  this._source = params.source;
  this._newPlayer = params.newPlayer;
  this._winType = params.wintype;

  //æ’­æ”¾é¡µä¸“é—¨å‚æ•°
  this._playlistconfig = params.playlistconfig;
  this._isMobile = YKP.isMobile;
  this._isMobileIOS = YKP.isMobileIOS;

  //this._weixin = params.weixin;
  YK.isWeixin = YKP.isWeixin; //false;
  //å¾®ä¿¡ä¸“ç”¨å‚æ•°
  if ('undefined' != typeof params.weixin) {
    YK.isWeixin = !!params.weixin; //!!Ã¥Â¤â€“Ã©Æ’Â¨Ã¤Â¼ Ã¥â€¦Â¥ weixin=fasle Ã¤Â¹Å¸Ã¥ÂÂ¯Ã¤Â»Â¥Ã§â€Å¸Ã¦â€¢Ë†
  }

  this._loop = !!params.loop || false;
  // more ..

  this._playerType = "";

};
YoukuPlayerSelect.prototype = {
  isPC: function() {
    return YKP.isPC;
  }, //todo
  select: function() {
    this.selectHandler();
  },
  selectHandler: function() {
    var url;
    if (this.isPC()) {
      YKP.isLoadFinishH5 = true;
    } else {
      //	dynamicLoading.js(YK.https + "//g.alicdn.com/ku/ykbannerLoader/1.0.01/js/ykbannerLoader.min.js", null, {"id":"ykbannerLoader", "pageType":"player", "isHidden":true});
      url = YK.https + "//player.youku.com/unifull/js/unifull.min.js?v=20190318";
    }
    if (YKP.isLoadFinishH5) {
      this.selectH5();
    } else {
      dynamicLoading.js(url, this);
    }


    if (this._events && this._events.onPlayerReady) {
      var callback = this._events.onPlayerReady;
      var check = setInterval(function() {
        // if ($(YKP.playerId)) {
        //     YKP.playerCurrentState = YKP.playerState.PLAYER_STATE_READY;
        //     debug.log(YKP.playerCurrentState);

        try {
          //    LocalStorage.appendItem('phase', 'playerready');
          callback();
        } catch (e) {}
        clearInterval(check);
        //}
      }, 500);
    }
  },
  selectH5: function() {
    if (YKP.isPC) {
      this.selectPCH5();
    } else {
      this.selectMobileH5();
    }
  },

  selectMobileH5: function() {
    var self = this;
    var playerDom = document.getElementById(this._target);
    if (this._width > 0 && this._height > 0) {
      playerDom.style.width = this._width + "px";
      playerDom.style.height = this._height + "px";
    } else {
      //var cw = document.documentElement.clientWidth;
      //var ch = document.documentElement.clientHeight;
      var cw = playerDom.offsetWidth;
      var ch = playerDom.offsetHeight;

      function resize(playerDom) {
        //playerDom.style.width = cw + "px";
        //playerDom.style.height = 9 * cw / 16 + "px";

        playerDom.style.width = cw + "px";
        playerDom.style.height = ch + "px";
      }
      resize(playerDom);
    }

    var closeFullFullScreen = 0;
    if (self._cancelFullScreen == 1 && YKP.isAndroidYouku) {
      closeFullFullScreen = 1;
    }

    var config = {
      videoId: self._vid, //è§†é¢‘id
      ccode: "0590", //æ¸ é“id
      client_id: self._partnerId, //ä¼˜é…·è§†é¢‘äº‘åˆ›å»ºåº”ç”¨çš„client_id
      control: {
        laguange: "", //é»˜è®¤ä½¿ç”¨çš„è¯­è¨€ç±»åž‹
        hd: "mp4hd", //é»˜è®¤ä½¿ç”¨çš„ç çŽ‡
        //   hd:"m3u8",
        autoplay: false //æ˜¯å¦è‡ªåŠ¨æ’­æ”¾
      },
      logconfig: {

      }, //ç»Ÿè®¡æ‰©å±•å‚æ•°ï¼ŒåŒ…æ‹¬aplusæŽ¥å£ä¸­çš„å…¨å±€å¯¹è±¡æ—¶æ•°æ®ï¼Œç”¨äºŽä¼ é€’ç»™ç»Ÿè®¡æŽ¥å£
      adConfig: {

      }, //å¹¿å‘Šæ‰©å±•å‚æ•°
      password: self._password, //è§†é¢‘æ’­æ”¾å¯†ç ï¼Œç”¨äºŽåŠ å¯†è§†é¢‘ï¼ˆè¿™ä¸ªæ˜¯å¦å¯ä»¥ä¼ å…¥æš‚å®šï¼‰
      wintype: "", //æ¯ç«¯å›ºå®šçš„å‚æ•°ï¼Œå¤šç”¨äºŽç»Ÿè®¡ï¼Œä¸ç¡®å®šæ˜¯å¦è¿˜éœ€è¦
      type: "", //æ’­æ”¾ç±»åž‹ï¼ˆpc,pad,mobileï¼‰æš‚å®š,
      events: self._events,

      embed_vid: self._embed_vid,
      embed_content: self._embed_content,
      titleStyle: self._titleStyle,
      source: self._source,
      closeFullFullScreen: closeFullFullScreen,
      isIphoneYouku: YKP.isIphoneYouku,
      imgPoster: self._poster
    };
    this._h5player = YKPlayer.Player(this._target, config);
  },

  selectPCH5: function() {
    var self = this;
    self.mobtest = 'mobtest';
    var cw;
    var ch;
    if (this._width > 0 && this._height > 0) {
      cw = this._width;
      ch = this._height;
    } else {
      //var playerDom = document.getElementById(this._target);
      //var cw = document.documentElement.clientWidth;
      //var ch = document.documentElement.clientHeight;
      //var cw = playerDom.offsetWidth;
      //var ch = playerDom.offsetHeight;
      cw = '100%';
      ch = '100%';

    }
    createIFrame(cw, ch, self._target, self._vid, self._partnerId, self._password, self._autoplay, self._events);

  },

  onorientationchange: function() {
    //var self = this;
    var playerDom = document.getElementById(this._target);
    setTimeout(function() {
      var cw = document.documentElement.clientWidth;
      var ch = document.documentElement.clientHeight;
      playerDom.style.width = cw + "px";
      playerDom.style.height = 9 * cw / 16 + "px";

    }, 300);
  },
  isThirdParty: function() {

    var cid = this._partnerId;
    if (cid != null && (cid + '').length == 16) {
      return true;
    };

    return false;
  },
};

/**
 * ä»¥ä¸‹æ˜¯ç»Ÿä¸€çš„æŽ¥å£ï¼Œç”¨äºŽå¤–éƒ¨ç»Ÿä¸€æ“ä½œ Flash å’Œ H5æ’­æ”¾å™¨
 *   ç›´æŽ¥ä¼ å…¥å‚æ•°è¿›è¡Œåˆå§‹åŒ–
 *    -- api document --
 *   //open.youku.com/docs/api/player
 *   ç”¨æˆ·åï¼šapi
 *   å¯†ç ï¼šyoukuopenapi
 *
 */
YKU.Player = function(target, config) {
  config.target = target;
  this.select = new YoukuPlayerSelect(config);
  this.select.select();
  this._player = "";
};
YKU.Player.prototype = {
  player: function() {
    if (this._player != "") {
      return this._player;
    }
    if (YKP.isPC) {
      this._player = new YKFlashPlayer();
    } else {
      this._player = new YKH5Player(this.select._h5player);
    }
    return this._player;
  },
  //@deprecated
  resize: function(dom, width, height) {
    if (dom && Number(width) && Number(height)) {
      dom.style ? dom.style.width = width + 'px' : null;
      dom.style ? dom.style.height = height + 'px' : null;
    } else {
      console.log('resizeæ–¹æ³•ä¸å¯ç”¨,ç¼ºå°‘å‚æ•°!');
    }
  },
  currentTime: function() {
    return this.player().currentTime();
  },
  totalTime: function() {
    return this.player().totalTime();
  },
  playVideo: function() {
    this.player().playVideo();
  },
  startPlayVideo: function() {
    this.player().startPlayVideo();
  },
  pauseVideo: function() {
    this.player().pauseVideo();
  },
  seekTo: function(timeoffset) {
    this.player().seekTo(timeoffset);
  },
  hideControls: function() {
    this.player().hideControls();
  },
  showControls: function() {
    this.player().showControls();
  },
  /** mute:function(){},
   unmute:function(){},
   setVolume:function(){},
   getVideoMetaData:function(){},*/
  playVideoById: function(vid) {
    this.player().playVideoById(vid);
  },
  //special api for youku h5,not open api
  switchFullScreen: function() {
    try {
      this.player().switchFullScreen();
    } catch (e) {

    }

  },
  getVideoList: function() {
    return this.player().getVideoList();
  }

};

var YKFlashPlayer = function() {
  this._player = document.getElementById(YKP.playerId);
};
YKFlashPlayer.prototype = {
  resize: function(width, height) {
    this._player.style.width = width + 'px';
    this._player.style.height = height + 'px';
  },
  currentTime: function() {
    var arr = this._player.getPlayerState().split("|");
    if (arr.length >= 3)
      return arr[2];
    else
      return -1;
  },
  totalTime: function() {
    var arr = this._player.getPlayerState().split("|");
    if (arr.length >= 4)
      return arr[3];
    else
      return -1;
  },
  playVideo: function() {
    this._player.pauseVideo(false);
  },
  pauseVideo: function() {
    this._player.pauseVideo(true);
  },
  seekTo: function(timeoffset) {
    this._player.nsseek(timeoffset);
  },
  playVideoById: function(vid) { //encoded vid  Ã¥Â­â€”Ã§Â¬Â¦Ã¤Â¸Â²Ã¥Â½Â¢Ã¥Â¼ÂÃ§Å¡â€žvid
    this._player.playVideoByID(vid);
  },
  hideControls: function() {
    this._player.showControlBar(false);
  },
  showControls: function() {
    this._player.showControlBar(true);
  },
  state: function() {
    this._player.state();
  }
};

/**
 * @param player  YoukuHTML5Player
 */
var YKH5Player = function(player) {

  this._player = player;
};
YKH5Player.prototype = {
  resize: function(width, height) {
    this._player.style.width = width + 'px';
    this._player.style.height = height + 'px';
  },
  currentTime: function() {
    return this._player.currentTime;
  },
  totalTime: function() {
    return this._player.totalTime;

  },
  playVideo: function() {
    this._player.play();
  },

  pauseVideo: function() {
    this._player.pause();
  },

  seekTo: function(timeoffset) {
    try {
      //  this._player.currentTime = timeoffset;
      this._player.seek(timeoffset);
    } catch (e) {}
  }
}

function executeScript(){
    var _scripts = document.getElementsByTagName("script"),_len = _scripts.length;
    for(var i = 0 ; i < _len ;i++){
        if(_scripts[i].src.indexOf("//player.youku.com/jsapi") > -1){
            if(_scripts[i].innerHTML){
              console.log('%cä¼˜é…·è§†é¢‘äº‘:æ’­æ”¾å™¨åˆå§‹åŒ–ä»£ç ï¼Œè¯·å•ç‹¬åœ¨æ–°çš„scriptæ ‡ç­¾å†…ã€‚å¦åˆ™ä¼šé€ æˆæ— æ³•æ’­æ”¾ï¼','color:red');
              eval(_scripts[i].innerHTML);
              break;
            }
        }
    }
}
executeScript();