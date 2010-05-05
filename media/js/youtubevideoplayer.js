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

/**
 *
 * @param {mirosubs.YoutubeVideoSource} videoSource
 */
mirosubs.YoutubeVideoPlayer = function(videoSource) {
    mirosubs.AbstractVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;
    this.playerAPIID_ = [videoSource.getUUID(), 
                         '' + new Date().getTime()].join('');
    this.playerElemID_ = videoSource.getUUID() + "_ytplayer";
    this.eventFunction_ = 'event' + videoSource.getUUID();

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
    this.swfEmbedded_ = false;
    this.progressTimer_ = new goog.Timer(
        mirosubs.AbstractVideoPlayer.PROGRESS_INTERVAL);
    this.timeUpdateTimer_ = new goog.Timer(
        mirosubs.AbstractVideoPlayer.TIMEUPDATE_INTERVAL);
};
goog.inherits(mirosubs.YoutubeVideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.YoutubeVideoPlayer.prototype.enterDocument = function() {
    mirosubs.YoutubeVideoPlayer.superClass_.enterDocument.call(this);
    if (!this.swfEmbedded_) {
        this.swfEmbedded_ = true;
        var videoDiv = this.getDomHelper().createDom('div');
        videoDiv.id = 'a' + this.makeId('video');
        this.getElement().appendChild(videoDiv);
        var params = { 'allowScriptAccess': 'always' };
        var atts = { 'id': this.playerElemID_ };
        window["swfobject"]["embedSWF"](
            ['http://www.youtube.com/v/', this.videoSource_.getYoutubeVideoID(), 
             '?enablejsapi=1&disablekb=1&playerapiid=', this.playerAPIID_].join(''),
            videoDiv.id, "480", "360", "8", null, null, params, atts);
    }
    this.getHandler().listen(
        this.progressTimer_, goog.Timer.TICK, this.progressTick_);
    this.getHandler().listen(
        this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
    this.progressTimer_.start();
    if (!this.isPaused())
        this.timeUpdateTimer_.start();
};
mirosubs.YoutubeVideoPlayer.prototype.exitDocument = function() {
    mirosubs.YoutubeVideoPlayer.superClass_.exitDocument.call(this);
    this.progressTimer_.stop();
    this.timeUpdateTimer_.stop();
};
mirosubs.YoutubeVideoPlayer.prototype.progressTick_ = function(e) {
    if (this.getDuration() > 0)
        this.dispatchEvent(
            mirosubs.AbstractVideoPlayer.EventType.PROGRESS);
};
mirosubs.YoutubeVideoPlayer.prototype.timeUpdateTick_ = function(e) {
    if (this.getDuration() > 0)
        this.dispatchEvent(
            mirosubs.AbstractVideoPlayer.EventType.TIMEUPDATE);
};
mirosubs.YoutubeVideoPlayer.prototype.onYouTubePlayerReady_ = function(playerAPIID) {
    if (playerAPIID == this.playerAPIID_) {
        this.player_ = goog.dom.$(this.playerElemID_);
        goog.array.forEach(this.commands_, function(cmd) { cmd(); });
        window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
        this.player_.addEventListener('onStateChange', this.eventFunction_);
    }
};
mirosubs.YoutubeVideoPlayer.prototype.playerStateChange_ = function(newState) {
    if (newState == mirosubs.YoutubeVideoPlayer.State_.PLAYING) {
        this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PLAY);
        this.timeUpdateTimer_.start();
    }
    else if (newState == mirosubs.YoutubeVideoPlayer.State_.PAUSED) {
        this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PAUSE);
        this.timeUpdateTimer_.stop();
    }
};
mirosubs.YoutubeVideoPlayer.prototype.getBufferedLength = function() {
    return this.getDuration() > 0  ? 1 : 0;
o};
mirosubs.YoutubeVideoPlayer.prototype.getBufferedStart = function(index) {
    return this.getDuration() * this.getStartBytes_() / this.getBytesTotal_();
};
mirosubs.YoutubeVideoPlayer.prototype.getBufferedEnd = function(index) {
    return this.getDuration() * 
        (this.getStartBytes_() + this.player_['getVideoBytesLoaded']()) /
        this.getBytesTotal_();
};
mirosubs.YoutubeVideoPlayer.prototype.getStartBytes_ = function() {
    return this.player_ ? this.player_['getVideoStartBytes']() : 0;
};
mirosubs.YoutubeVideoPlayer.prototype.getBytesTotal_ = function() {
    return this.player_ ? this.player_['getVideoBytesTotal']() : 0;
};
mirosubs.YoutubeVideoPlayer.prototype.getDuration = function() {
    return this.player_ ? this.player_['getDuration']() : 0;
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
mirosubs.YoutubeVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.YoutubeVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
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