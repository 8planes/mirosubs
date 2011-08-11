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
    mirosubs.video.FlashVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;
    this.playerAPIID_ = [videoSource.getUUID(),
                         '' + new Date().getTime()].join('');
    this.playerElemID_ = videoSource.getUUID() + "_ytplayer";
    this.eventFunction_ = 'event' + videoSource.getUUID();
    this.forDialog_ = !!opt_forDialog;

    mirosubs.video.YoutubeVideoPlayer.players_.push(this);

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
goog.inherits(mirosubs.video.YoutubeVideoPlayer, mirosubs.video.FlashVideoPlayer);

mirosubs.video.YoutubeVideoPlayer.players_ = [];
mirosubs.video.YoutubeVideoPlayer.readyAPIIDs_ = new goog.structs.Set();

mirosubs.video.YoutubeVideoPlayer.prototype.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.video.YoutubeVideoPlayer');

/**
 * @override
 */
mirosubs.video.YoutubeVideoPlayer.prototype.isFlashElementReady = function(elem) {
    return elem['playVideo'];
};

mirosubs.video.YoutubeVideoPlayer.prototype.windowReadyAPIIDsContains = function(apiID) {
    // this is activated if a widgetizer user has inserted the widgetizerprimer
    // into the HEAD of their document.
    var arr = window['unisubs_readyAPIIDs'];
    return arr && goog.array.contains(arr, apiID);
};

mirosubs.video.YoutubeVideoPlayer.prototype.decorateInternal = function(elem) {
    mirosubs.video.YoutubeVideoPlayer.superClass_.decorateInternal.call(this, elem);
    this.swfEmbedded_ = true;
    var apiidMatch = /playerapiid=([^&]+)/.exec(mirosubs.Flash.swfURL(elem));
    this.playerAPIID_ = apiidMatch ? apiidMatch[1] : '';
    if (mirosubs.video.YoutubeVideoPlayer.readyAPIIDs_.contains(this.playerAPIID_) ||
        this.windowReadyAPIIDsContains(this.playerAPIID_))
        this.onYouTubePlayerReady_(this.playerAPIID_);
    this.playerSize_ = goog.style.getSize(this.getElement());
    this.setDimensionsKnownInternal();
    if (goog.DEBUG) {
        this.logger_.info("In decorateInternal, a containing element size of " + 
                          this.playerSize_);
    }
};

/**
 * @override
 */
mirosubs.video.YoutubeVideoPlayer.prototype.setFlashPlayerElement = function(elem) {
    this.player_ = elem;
    window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
    this.player_.addEventListener(
        'onStateChange', this.eventFunction_);
};

mirosubs.video.YoutubeVideoPlayer.prototype.createDom = function() {
    mirosubs.video.YoutubeVideoPlayer.superClass_.createDom.call(this);
    var sizeFromConfig = this.videoSource_.sizeFromConfig();
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
        var params = { 'allowScriptAccess': 'always', 
                       'wmode' : 'opaque', 
                       'allowFullScreen': 'true' };
        var atts = { 'id': this.playerElemID_, 
                     'style': mirosubs.style.setSizeInString(
                         '', this.playerSize_) };
        var uri;
        if (this.forDialog_)
            uri = new goog.Uri('http://www.youtube.com/apiplayer');
        else
            uri = new goog.Uri(
                'http://www.youtube.com/v/' +
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
    if (goog.DEBUG) {
        this.logger_.info(
            "onYouTubePlayerReady_ called with an id of " + playerAPIID +
                ". My id is " + this.playerAPIID_ + ".");
    }
    if (playerAPIID != this.playerAPIID_)
        return;
    if (!this.isDecorated()) {
        this.setDimensionsKnownInternal();
        this.player_ = goog.dom.getElement(this.playerElemID_);
        mirosubs.style.setSize(this.player_, this.playerSize_);
        if (this.forDialog_)
            this.player_['cueVideoById'](this.videoSource_.getYoutubeVideoID());
        goog.array.forEach(this.commands_, function(cmd) { cmd(); });
        this.commands_ = [];
        window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
        this.player_.addEventListener('onStateChange', this.eventFunction_);
    }
    else {
        if (goog.DEBUG) {
            this.logger_.info("In playerReady, a containing element size of " + 
                              goog.style.getSize(this.getElement()));
            this.logger_.info("In playerReady, a sizing element size of " + 
                              goog.style.getSize(this.getElement()));
        }
        this.tryDecoratingAll();
    }
};
mirosubs.video.YoutubeVideoPlayer.prototype.playerStateChange_ = function(newState) {
    var s = mirosubs.video.YoutubeVideoPlayer.State_;
    var et = mirosubs.video.AbstractVideoPlayer.EventType;
    this.logger_.info("player new state is " + newState);
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

mirosubs.video.YoutubeVideoPlayer.prototype.setPlayheadTime = function(playheadTime, skipsUpdateEvent)
{
    if (this.player_) {
        this.player_['seekTo'](playheadTime, true);
        if (!skipsUpdateEvent)this.sendTimeUpdateInternal();
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
    if (goog.DEBUG) {
        this.logger_.info('getVideoSize returning ' + this.playerSize_);
    }
    return this.playerSize_;
};
mirosubs.video.YoutubeVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.YoutubeVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
};
mirosubs.video.YoutubeVideoPlayer.prototype.getVideoElement = function() {
    return goog.dom.getElement(this.playerElemID_);
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

mirosubs.video.YoutubeVideoPlayer.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.video.YoutubeVideoPlayerStatic');

(function() {
    var ytReady = "onYouTubePlayerReady";
    var oldReady = window[ytReady] || goog.nullFunction;
    window[ytReady] = function(apiID) {
        if (goog.DEBUG) {
            mirosubs.video.YoutubeVideoPlayer.logger_.info(
                'onYouTubePlayerReady for ' + apiID);
            mirosubs.video.YoutubeVideoPlayer.logger_.info(
                'players_ length is ' + 
                    mirosubs.video.YoutubeVideoPlayer.players_.length);
        }
        try {
            oldReady(apiID);
        }
        catch (e) {
            // don't care
        }
        if (apiID == 'undefined' || !goog.isDefAndNotNull(apiID))
            apiID = '';
        mirosubs.video.YoutubeVideoPlayer.readyAPIIDs_.add(apiID);
        goog.array.forEach(
            mirosubs.video.YoutubeVideoPlayer.players_,
            function(p) { p.onYouTubePlayerReady_(apiID); });
    };
})();
