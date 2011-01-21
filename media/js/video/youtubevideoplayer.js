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

goog.provide('mirosubs.video.YoutubeVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.YoutubeVideoSource} videoSource
 * @param {boolean=} opt_forDialog
 */
mirosubs.video.YoutubeVideoPlayer = function(videoSource, opt_forDialog) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;
    this.playerAPIID_ = [videoSource.getUUID(),
                         '' + new Date().getTime()].join('');
    this.playerElemID_ = videoSource.getUUID() + "_ytplayer";
    this.eventFunction_ = 'event' + videoSource.getUUID();
    this.forDialog_ = !!opt_forDialog;

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
    this.playerSize_ = null;
    this.player_ = null;
    /**
     * Array of functions to execute once player is ready.
     */
    this.commands_ = [];
    this.swfEmbedded_ = false;
    this.progressTimer_ = new goog.Timer(
        mirosubs.video.AbstractVideoPlayer.PROGRESS_INTERVAL);
    this.timeUpdateTimer_ = new goog.Timer(
        mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL);
};
goog.inherits(mirosubs.video.YoutubeVideoPlayer, mirosubs.video.AbstractVideoPlayer);

mirosubs.video.YoutubeVideoPlayer.logger_ =
    goog.debug.Logger.getLogger('YoutubeVideoPlayer');

/**
 * For FF, this decorates an Embed element.
 * @override
 * @param {Element} element Either object or embed for yt video. Must 
 *     have enablejsapi=1.
 */
mirosubs.video.YoutubeVideoPlayer.prototype.decorateInternal = function(element) {
    mirosubs.video.YoutubeVideoPlayer.superClass_.decorateInternal.call(
        this, element);
    this.swfEmbedded_ = true;
    this.player_ = element;
    this.playerSize_ = goog.style.getSize(element);
    mirosubs.video.YoutubeVideoPlayer.logger_.info(
        ["height, width of ", this.playerSize_.height, ", ", 
         this.playerSize_.width].join(''));
    this.setDimensionsKnownInternal();
    // FIXME: petit duplication
    window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
    var timer = new goog.Timer(200);
    var that = this;
    this.getHandler().listen(
        timer,
        goog.Timer.TICK,
        function(e) {
            if (that.player_['playVideo']) {
                mirosubs.video.YoutubeVideoPlayer.logger_.info(
                    'playVideo is present');
                that.player_.addEventListener(
                    'onStateChange', that.eventFunction_);
                timer.stop();
            }
        });
    timer.start();
};

mirosubs.video.YoutubeVideoPlayer.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper().createElement('span'));
    var sizeFromConfig = this.sizeFromConfig_();
    if (!this.forDialog_ && sizeFromConfig)
        this.playerSize_ = sizeFromConfig;
    else
        this.playerSize_ = this.forDialog_ ?
        mirosubs.video.AbstractVideoPlayer.DIALOG_SIZE :
        mirosubs.video.AbstractVideoPlayer.DEFAULT_SIZE;    
};

mirosubs.video.YoutubeVideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.YoutubeVideoPlayer.superClass_.enterDocument.call(this);
    if (!this.swfEmbedded_) {
        this.swfEmbedded_ = true;
        var videoSpan = this.getDomHelper().createDom('span');
        videoSpan.id = mirosubs.randomString();
        this.getElement().appendChild(videoSpan);
        var params = { 'allowScriptAccess': 'always', 'wmode' : 'opaque' };
        var atts = { 'id': this.playerElemID_, 
                     'style': mirosubs.style.setSizeInString(
                         '', this.playerSize_) };
        var uri;
        if (this.forDialog_)
            uri = new goog.Uri('http://www.youtube.com/apiplayer');
        else
            uri = new goog.Uri('http://www.youtube.com/v/' +
                               this.videoSource_.getYoutubeVideoID());
        this.addQueryString_(uri);
        window["swfobject"]["embedSWF"](
            uri.toString(), videoSpan.id, 
            this.playerSize_.width + '', 
            this.playerSize_.height + '', 
            "8", null, null, params, atts);
    }
    this.getHandler().
        listen(this.progressTimer_, goog.Timer.TICK, this.progressTick_).
        listen(this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
    this.progressTimer_.start();
};
mirosubs.video.YoutubeVideoPlayer.prototype.addQueryString_ = function(uri) {
    var config = this.videoSource_.getVideoConfig();
    if (!this.forDialog_ && config) {
        for (var prop in config)
            if (prop != 'width' && prop != 'height')
                uri.setParameterValue(prop, config[prop])
    }
    uri.setParameterValue('enablejsapi', '1').
        setParameterValue('version', '3').
        setParameterValue('playerapiid', this.playerAPIID_);
    if (this.forDialog_)
        uri.setParameterValue('disablekb', '1');
};
mirosubs.video.YoutubeVideoPlayer.prototype.sizeFromConfig_ = function() {
    var config = this.videoSource_.getVideoConfig();
    if (config && config['width'] && config['height'])
        return new goog.math.Size(
            parseInt(config['width']), parseInt(config['height']));
    else
        return null;
};
mirosubs.video.YoutubeVideoPlayer.prototype.exitDocument = function() {
    mirosubs.video.YoutubeVideoPlayer.superClass_.exitDocument.call(this);
    this.progressTimer_.stop();
    this.timeUpdateTimer_.stop();
};
mirosubs.video.YoutubeVideoPlayer.prototype.progressTick_ = function(e) {
    if (this.getDuration() > 0)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PROGRESS);
};
mirosubs.video.YoutubeVideoPlayer.prototype.timeUpdateTick_ = function(e) {
    if (this.getDuration() > 0)
        this.sendTimeUpdateInternal();
};
mirosubs.video.YoutubeVideoPlayer.prototype.onYouTubePlayerReady_ =
    function(playerAPIID)
{
    if (playerAPIID == this.playerAPIID_) {
        this.setDimensionsKnownInternal();
        this.player_ = goog.dom.$(this.playerElemID_);
        mirosubs.video.YoutubeVideoPlayer.logger_.info('setting size');
        mirosubs.style.setSize(this.player_, this.playerSize_);
        if (this.forDialog_)
            this.player_['cueVideoById'](this.videoSource_.getYoutubeVideoID());
        goog.array.forEach(this.commands_, function(cmd) { cmd(); });
        this.commands_ = [];
        window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
        this.player_.addEventListener('onStateChange', this.eventFunction_);
    }
};
mirosubs.video.YoutubeVideoPlayer.prototype.playerStateChange_ = function(newState) {
    mirosubs.video.YoutubeVideoPlayer.logger_.info('playerStateChange');
    var s = mirosubs.video.YoutubeVideoPlayer.State_;
    var et = mirosubs.video.AbstractVideoPlayer.EventType;
    if (newState == s.PLAYING) {
        this.dispatchEvent(et.PLAY);
        this.timeUpdateTimer_.start();
    }
    else if (newState == s.PAUSED) {
        this.dispatchEvent(et.PAUSE);
        this.timeUpdateTimer_.stop();
    }
    else if (newState == s.ENDED)
        this.dispatchEndedEvent();
};
mirosubs.video.YoutubeVideoPlayer.prototype.getBufferedLength = function() {
    return this.getDuration() > 0  ? 1 : 0;
};
mirosubs.video.YoutubeVideoPlayer.prototype.getBufferedStart = function(index) {
    var startBytes = this.getStartBytes_();
    return this.getDuration() * startBytes / (startBytes + this.getBytesTotal_());
};
mirosubs.video.YoutubeVideoPlayer.prototype.getBufferedEnd = function(index) {
    var startBytes = this.getStartBytes_();
    return this.getDuration() *
        (startBytes + this.player_['getVideoBytesLoaded']()) /
        (startBytes + this.getBytesTotal_());
};
mirosubs.video.YoutubeVideoPlayer.prototype.getStartBytes_ = function() {
    return this.player_ ? this.player_['getVideoStartBytes']() : 0;
};
mirosubs.video.YoutubeVideoPlayer.prototype.getBytesTotal_ = function() {
    return this.player_ ? this.player_['getVideoBytesTotal']() : 0;
};
mirosubs.video.YoutubeVideoPlayer.prototype.getDuration = function() {
    if (!this.duration_) {
        this.duration_ = 
            (this.player_ && this.player_['getDuration']) ? 
                this.player_['getDuration']() : 0;
        if (this.duration_ <= 0)
            this.duration_ = 0;
    }
    return this.duration_;
};
mirosubs.video.YoutubeVideoPlayer.prototype.getVolume = function() {
    return this.player_ ? (this.player_['getVolume']() / 100) : 0;
};
mirosubs.video.YoutubeVideoPlayer.prototype.setVolume = function(vol) {
    if (this.player_)
        this.player_['setVolume'](vol * 100);
    else
        this.commands_.push(goog.bind(this.setVolume_, this, vol));
};
mirosubs.video.YoutubeVideoPlayer.prototype.isPausedInternal = function() {
    return this.getPlayerState_() == mirosubs.video.YoutubeVideoPlayer.State_.PAUSED;
};
mirosubs.video.YoutubeVideoPlayer.prototype.videoEndedInternal = function() {
    return this.getPlayerState_() == mirosubs.video.YoutubeVideoPlayer.State_.ENDED;
};
mirosubs.video.YoutubeVideoPlayer.prototype.isPlayingInternal = function() {
    return this.getPlayerState_() == mirosubs.video.YoutubeVideoPlayer.State_.PLAYING;
};
mirosubs.video.YoutubeVideoPlayer.prototype.playInternal = function () {
    if (this.player_)
        this.player_['playVideo']();
    else
        this.commands_.push(goog.bind(this.playInternal, this));
};
mirosubs.video.YoutubeVideoPlayer.prototype.pauseInternal = function() {
    if (this.player_)
        this.player_['pauseVideo']();
    else
        this.commands_.push(goog.bind(this.pauseInternal, this));
};
mirosubs.video.YoutubeVideoPlayer.prototype.stopLoadingInternal = function() {
    if (this.player_) {
        this.player_['stopVideo']();
	this.setLoadingStopped(true);
	return true;	
    }
    else {
	this.commands_.push(goog.bind(this.stopLoadingInternal, this));
	return false;
    }
};
mirosubs.video.YoutubeVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    if (this.player_) {
        this.player_['cueVideoById'](this.videoSource_.getYoutubeVideoID(), playheadTime);
	this.setLoadingStopped(false);
    }
    else
        this.commands_.push(goog.bind(this.resumeLoadingInternal, this, playheadTime));
};
mirosubs.video.YoutubeVideoPlayer.prototype.getPlayheadTime = function() {
    return this.player_ ? this.player_['getCurrentTime']() : 0;
};
mirosubs.video.YoutubeVideoPlayer.prototype.setPlayheadTime = function(playheadTime)
{
    if (this.player_) {
        this.player_['seekTo'](playheadTime, true);
        this.sendTimeUpdateInternal();
    }
    else
        this.commands_.push(goog.bind(this.setPlayheadTime,
                                      this, playheadTime));
};
mirosubs.video.YoutubeVideoPlayer.prototype.getPlayerState_ = function() {
    return this.player_ ? this.player_['getPlayerState']() : -1;
};
mirosubs.video.YoutubeVideoPlayer.prototype.needsIFrame = function() {
    return goog.userAgent.LINUX;
};
mirosubs.video.YoutubeVideoPlayer.prototype.getVideoSize = function() {
    return this.playerSize_;
};
mirosubs.video.YoutubeVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.YoutubeVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
};
mirosubs.video.YoutubeVideoPlayer.prototype.getVideoElement = function() {
    return this.player_;
};
/**
 * http://code.google.com/apis/youtube/js_api_reference.html#getPlayerState
 * @enum
 */
mirosubs.video.YoutubeVideoPlayer.State_ = {
    UNSTARTED: -1,
    ENDED: 0,
    PLAYING: 1,
    PAUSED: 2,
    BUFFERING: 3,
    VIDEO_CUED: 5
};