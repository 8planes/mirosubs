// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('mirosubs.YoutubeVideoPlayer');

mirosubs.YoutubeVideoPlayer = function(uuid, divID, youtubeVideoID) {
    mirosubs.AbstractVideoPlayer.call(this);
    this.playerElemID = uuid + "_ytplayer";
    this.playerAPIID = [uuid, '_', '' + new Date().getTime()].join('');
    this.eventFunction_ = ['event', uuid].join('');

    var readyFunc = goog.bind(this.onYouTubePlayerReady_, this);
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
    var atts = { 'id': this.playerElemID };
    this.videoDiv_ = goog.dom.$(divID).parentNode;
    swfobject.embedSWF(['http://www.youtube.com/v/', 
                        youtubeVideoID, 
                        '?enablejsapi=1&playerapiid=',
                        this.playerAPIID].join(''),
                       divID, "480", "360", "8", null, null, params, atts);
};
goog.inherits(mirosubs.YoutubeVideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.YoutubeVideoPlayer.prototype.onYouTubePlayerReady_ = function(playerAPIID) {
    if (playerAPIID == this.playerAPIID) {
        this.player_ = goog.dom.$(this.playerElemID);
        goog.array.forEach(this.commands_, 
                           function(cmd) {
                               cmd();
                           });
        window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
        this.player_.addEventListener('onStateChange', this.eventFunction_);
    }
};

mirosubs.YoutubeVideoPlayer.prototype.playerStateChange_ = function(newState) {
    if (newState == mirosubs.YoutubeVideoPlayer.State_.PLAYING)
        this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PLAY);
    else if (newState == mirosubs.YoutubeVideoPlayer.State_.PAUSED)
        this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PAUSE);
};

mirosubs.YoutubeVideoPlayer.prototype.isPaused = function() {
    return this.getPlayerState_() == mirosubs.YoutubeVideoPlayer.State_.PAUSED;
};
mirosubs.YoutubeVideoPlayer.prototype.videoEnded = function() {
    return this.getPlayerState_() == mirosubs.YoutubeVideoPlayer.State_.ENDED;
};
mirosubs.YoutubeVideoPlayer.prototype.isPlaying = function() {
    return this.getPlayerState_() == mirosubs.YoutubeVideoPlayer.State_.PLAYING;
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
/**
 * http://code.google.com/apis/youtube/js_api_reference.html#getPlayerState
 * @enum
 */
mirosubs.YoutubeVideoPlayer.State_ = {
    UNSTARTED: -1,
    ENDED: 0,
    PLAYING: 1,
    PAUSED: 2,
    BUFFERING: 3,
    VIDEO_CUED: 5
};