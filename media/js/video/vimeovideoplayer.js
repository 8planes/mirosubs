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

goog.provide('mirosubs.video.VimeoVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.VimeoVideoSource} videoSource
 * @param {boolean=} opt_chromeless
 */
mirosubs.video.VimeoVideoPlayer = function(videoSource) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;

    this.player_ = null;
    this.playerAPIID_ = [videoSource.getUUID(),
                         '' + new Date().getTime()].join('');
    this.playerElemID_ = videoSource.getUUID() + "_vimeoplayer";
    this.eventFunction_ = 'event' + videoSource.getUUID();
    
    this.currentVolume_ = 0;
    this.loadedFraction_ = 0;

    var readyFunc = goog.bind(this.onVimeoPlayerReady_, this);
    var vpReady = "vimeo_player_loaded";
    if (window[vpReady]) {
        var oldReady = window[vpReady];
        window[vpReady] = function(playerAPIID) {
            oldReady(playerAPIID);
            readyFunc(playerAPIID);
        };
    }
    else
        window[vpReady] = readyFunc;

    this.player_ = null;
    /**
     * Array of functions to execute once player is ready.
     */
    this.commands_ = [];
    this.swfEmbedded_ = false;
    this.timeUpdateTimer_ = new goog.Timer(
        mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL);
};
goog.inherits(mirosubs.video.VimeoVideoPlayer, mirosubs.video.AbstractVideoPlayer);

mirosubs.video.VimeoVideoPlayer.WIDTH = 400;
mirosubs.video.VimeoVideoPlayer.HEIGHT = 300;

mirosubs.video.VimeoVideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.VimeoVideoPlayer.superClass_.enterDocument.call(this);
    if (!this.swfEmbedded_) {
        this.swfEmbedded_ = true;
        var videoDiv = this.getDomHelper().createDom('div');
        videoDiv.id = mirosubs.randomString();
        this.getElement().appendChild(videoDiv);
        var params = { 'allowScriptAccess': 'always', 'wmode' : 'opaque' };
        var atts = { 'id': this.playerElemID_ };
        var baseURL = 'http://vimeo.com/moogaloop.swf';
        var queryString =
            ['?js_api=1&width=', mirosubs.video.VimeoVideoPlayer.WIDTH,
             '&height=', mirosubs.video.VimeoVideoPlayer.HEIGHT,
             '&clip_id=', this.videoSource_.getVideoId(),
             '&js_swf_id=', this.playerAPIID_].join('');
        this.setDimensionsKnownInternal();
        window["swfobject"]["embedSWF"](
            [baseURL, queryString].join(''),
            videoDiv.id, mirosubs.video.VimeoVideoPlayer.WIDTH,
            mirosubs.video.VimeoVideoPlayer.HEIGHT, "8",
            null, null, params, atts);
    }
    this.getHandler().
        listen(this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
};
mirosubs.video.VimeoVideoPlayer.prototype.exitDocument = function() {
    mirosubs.video.VimeoVideoPlayer.superClass_.exitDocument.call(this);
    this.timeUpdateTimer_.stop();
};

mirosubs.video.VimeoVideoPlayer.prototype.getPlayheadTimeInternal = function() {
    return this.swfLoaded_ ? this.player_['api_getCurrentTime']() : 0;
};

mirosubs.video.VimeoVideoPlayer.prototype.timeUpdateTick_ = function(e) {
    if (this.getDuration() > 0)
        this.sendTimeUpdateInternal();
};

mirosubs.video.VimeoVideoPlayer.prototype.getDuration = function() {
    return this.player_['api_getDuration']();
};

mirosubs.video.VimeoVideoPlayer.prototype.getBufferedLength = function() {
    return this.player_ ? 1 : 0;
};
mirosubs.video.VimeoVideoPlayer.prototype.getBufferedStart = function(index) {
    // vimeo seems to only buffer from the start
    return 0;
};
mirosubs.video.VimeoVideoPlayer.prototype.getBufferedEnd = function(index) {
    return this.loadedFraction_ * this.getDuration();
};

// vimeo doesn't let us get the current volume, only set it
mirosubs.video.VimeoVideoPlayer.prototype.getVolume = function() {
    return this.currentVolume_;
};
mirosubs.video.VimeoVideoPlayer.prototype.setVolume = function(volume) {
    if (this.player_) {
        this.player_['api_setVolume'](100 * volume);
        this.currentVolume_ = volume;
    }
    else
        this.commands_.push(goog.bind(this.setVolume, this, volume));
};

mirosubs.video.VimeoVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    if (this.player_) {
        this.player_['api_seekTo'](playheadTime);
        this.sendTimeUpdateInternal();
    }
    else
        this.commands_.push(goog.bind(this.setPlayheadTime, this, playheadTime));
};

mirosubs.video.VimeoVideoPlayer.prototype.getVideoSize = function() {
    return new goog.math.Size(mirosubs.video.VimeoVideoPlayer.WIDTH,
                              mirosubs.video.VimeoVideoPlayer.HEIGHT);
};

mirosubs.video.VimeoVideoPlayer.prototype.isPausedInternal = function() {
    return !this.isPlaying_;
};
mirosubs.video.VimeoVideoPlayer.prototype.isPlayingInternal = function() {
    return this.isPlaying_;
};
mirosubs.video.VimeoVideoPlayer.prototype.videoEndedInternal = function() {
    return this.getPlayheadTime() == this.getDuration();
};
mirosubs.video.VimeoVideoPlayer.prototype.playInternal = function() {
    if (this.swfLoaded_)
        this.player_['api_play']();
    else
        this.commands_.push(goog.bind(this.playInternal, this));
};
mirosubs.video.VimeoVideoPlayer.prototype.pauseInternal = function() {
    if (this.swfLoaded_)
        this.player_['api_pause']();
    else
        this.commands_.push(goog.bind(this.pauseInternal, this));
};

mirosubs.video.VimeoVideoPlayer.prototype.stopLoadingInternal = function() {
    this.pause();
};
mirosubs.video.VimeoVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    this.play();
};



mirosubs.video.VimeoVideoPlayer.prototype.onVimeoPlayerReady_ = function(swf_id) {
    if (swf_id != this.playerAPIID_)
        return;

    this.player_ = goog.dom.$(this.playerElemID_);
    this.setVolume(0.5);
    this.swfLoaded_ = true;
    goog.array.forEach(this.commands_, function(cmd) { cmd(); });
    this.commands_ = [];
    
    var that = this;

    var randomString = mirosubs.randomString();

    var onLoadingFn = "onVimeoLoa" + randomString;
    window[onLoadingFn] = function(data, swf_id) {
        that.loadedFraction_ = data;
        that.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PROGRESS);
    };
    this.player_['api_addEventListener']('onLoading', onLoadingFn);

    var onFinishFn = "onVimeoFin" + randomString;
    window[onFinishFn] = function(data, swf_id) {
        that.dispatchEndedEvent();
    };
    this.player_['api_addEventListener']('onFinish', onFinishFn);

    var onPlayFn = "onVimeoPla" + randomString;
    window[onPlayFn] = function(swfID) {
        that.isPlaying_ = true;
        that.timeUpdateTimer_.start();
    };
    this.player_['api_addEventListener']('onPlay', onPlayFn);

    var onPauseFn = "onVimeoPau" + randomString;
    window[onPauseFn] = function(swfID) {
        that.isPlaying_ = false;
        that.timeUpdatetimer_.stop();
    };
    this.player_['api_addEventListener']('onPause', onPauseFn);
};

mirosubs.video.VimeoVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.VimeoVideoPlayer.superClass_.disposeInternal.call(this);
    this.timeUpdateTimer_.dispose();
};
