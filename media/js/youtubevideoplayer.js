goog.provide('mirosubs.YoutubeVideoPlayer');

mirosubs.YoutubeVideoPlayer = function(uuid, divID, youtubeVideoID) {
    mirosubs.AbstractVideoPlayer.call(this);
    var playerElemID = uuid + "_ytplayer";
    var thisPlayerAPIID = [uuid, '_', '' + new Date().getTime()].join();
    var that = this;
    var readyFunc = function(playerAPIID) {
        if (playerAPIID == thisPlayerAPIID)
            that.setPlayer_(playerElemID);
    };
    var ytReady = "onYouTubePlayerReady";
    if (window[ytReady]) {
        var oldReady = window[ytReady];
        window[ytReady] = function(playerAPIID) {
            oldReady(playerAPIID);
            readyFunc(playerAPIID);
        };
    }
    else
        window[ytReady] = readyFunc;

    this.player_ = null;
    /**
     * Array of functions to execute once player is ready.
     */
    this.commands_ = [];
    var params = { 'allowScriptAccess': 'always' };
    var atts = { 'id': playerElemID };
    this.videoDiv_ = goog.dom.$(divID).parentNode;
    swfobject.embedSWF(['http://www.youtube.com/v/', 
                        youtubeVideoID, 
                        '?enablejsapi=1&playerapiid=',
                        thisPlayerAPIID].join(''),
                       divID, "480", "360", "8", null, null, params, atts);
};
goog.inherits(mirosubs.YoutubeVideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.YoutubeVideoPlayer.prototype.setPlayer_ = function(elemID) {
    this.player_ = goog.dom.$(elemID);
    goog.array.forEach(this.commands_, 
                       function(cmd) {
                           cmd();
                       });
};
mirosubs.YoutubeVideoPlayer.prototype.isPaused = function() {
    return this.getPlayerState_() == 2;
};
mirosubs.YoutubeVideoPlayer.prototype.videoEnded = function() {
    return this.getPlayerState_() == 0;
};
mirosubs.YoutubeVideoPlayer.prototype.play = function () {
    if (this.player_)
        this.player_['playVideo']();
    else
        this.commands_.push(goog.bind(this.play, this));
};
mirosubs.YoutubeVideoPlayer.prototype.pause = function() {
    if (this.player_)
        this.player_['pauseVideo']();
    else
        this.commands_.push(goog.bind(this.pause, this));
};
mirosubs.YoutubeVideoPlayer.prototype.getPlayheadTime = function() {
    return this.player_ ? this.player_['getCurrentTime']() : 0;
};
mirosubs.YoutubeVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    if (this.player_)
        this.player_['seekTo'](playheadTime, true);
    else
        this.commands_.push(goog.bind(this.setPlayheadTime, 
                                      this, playheadTime));
};
mirosubs.YoutubeVideoPlayer.prototype.getPlayerState_ = function() {
    return this.player_ ? this.player_['getPlayerState']() : -1;
};
mirosubs.YoutubeVideoPlayer.prototype.needsIFrame = function() {
    return goog.userAgent.LINUX;
};
mirosubs.YoutubeVideoPlayer.prototype.getVideoSize = function() {
    return new goog.math.Size(480, 360);
};
mirosubs.YoutubeVideoPlayer.prototype.getVideoContainerElem = function() {
    return this.videoDiv_;
};