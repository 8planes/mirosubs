goog.provide('mirosubs.YoutubeVideoPlayer');

mirosubs.YoutubeVideoPlayer = function(uuid, divID, youtubeVideoID) {
    mirosubs.AbstractVideoPlayer.call(this);
    var ytid = uuid + "_ytplayer";
    var params = { 'allowScriptAccess': 'always' };
    var atts = { 'id': ytid };
    swfobject.embedSWF(['http://www.youtube.com/v/', 
                        youtubeVideoID,'?enablejsapi=1'].join(''),
                       divID, "480", "360", "8", null, null, params, atts);
    this.player_ = goog.dom.$(ytid);
};
goog.inherits(mirosubs.YoutubeVideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.YoutubeVideoPlayer.prototype.isPaused = function() {
    return this.getPlayerState_() == 2;
};
mirosubs.YoutubeVideoPlayer.prototype.videoEnded = function() {
    return this.getPlayerState_() == 0;
};
mirosubs.YoutubeVideoPlayer.prototype.play = function () {
    this.player_['playVideo']();
};
mirosubs.YoutubeVideoPlayer.prototype.pause = function() {
    this.player_['pauseVideo']();
};
mirosubs.YoutubeVideoPlayer.prototype.getPlayheadTime = function() {
    return this.player_['getCurrentTime']();
};
mirosubs.YoutubeVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    return this.player_['seekTo'](playheadTime, true);
};
mirosubs.YoutubeVideoPlayer.prototype.showCaptionText = function(text) {
    // TODO: implement me
};
mirosubs.YoutubeVideoPlayer.prototype.getPlayerState_ = function() {
    return this.player_['getPlayerState']();
};