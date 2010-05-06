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

goog.provide('mirosubs.Html5VideoPlayer');

/**
 *
 * @param {mirosubs.Html5VideoSource} videoSource
 */
mirosubs.Html5VideoPlayer = function(videoSource) {
    mirosubs.AbstractVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;
    this.videoElem_ = null;
    this.progressThrottle_ = new goog.Throttle(
        this.videoProgress_, 
        mirosubs.AbstractVideoPlayer.PROGRESS_INTERVAL,
        this);
    this.timeUpdateThrottle_ = new goog.Throttle(
        this.videoTimeUpdate_, 
        mirosubs.AbstractVideoPlayer.TIMEUPDATE_INTERVAL,
        this);
};
goog.inherits(mirosubs.Html5VideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.Html5VideoPlayer.WIDTH = 400;
mirosubs.Html5VideoPlayer.HEIGHT = 300;

mirosubs.Html5VideoPlayer.prototype.createDom = function() {
    mirosubs.Html5VideoPlayer.superClass_.createDom.call(this);
    this.getElement().style.height = mirosubs.Html5VideoPlayer.HEIGHT + 'px';
    this.addVideoElement_(this.getElement(), true);
};
mirosubs.Html5VideoPlayer.prototype.decorateInternal = function(el) {
    mirosubs.Html5VideoPlayer.superClass_.decorateInternal.call(this, el);
    this.addVideoElement_(el, false);
};
mirosubs.Html5VideoPlayer.prototype.addVideoElement_ = function(el, hardCodeWidth) {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var testVideo = $d('video');
    if (typeof(testVideo['canPlayType']) != 'undefined') {
        var params = {'autobuffer': 'true', 'controls': 'true' };
        if (hardCodeWidth)
            params['width'] = mirosubs.Html5VideoPlayer.WIDTH;
        el.appendChild(
            this.videoElem_ = 
                $d('video', params,
                   $d('source', {'src': this.videoSource_.getVideoURL()})));
    }
    else {
        el.style.width = '400px';
        el.style.height = '300px';
        el.style.lineHeight = '300px';
        el.innerHTML = "Sorry, your browser can't play HTML5/Ogg video. " +
            "<a href='http://getfirefox.com'>Get Firefox</a>.";
    }
};
mirosubs.Html5VideoPlayer.prototype.enterDocument = function() {
    this.getHandler().listen(
        this.videoElem_, 'play', this.videoPlaying_);
    this.getHandler().listen(
        this.videoElem_, 'pause', this.videoPaused_);
    this.getHandler().listen(
        this.videoElem_, 'progress', 
        this.progressThrottle_.fire, false, this.progressThrottle_);
    this.getHandler().listen(
        this.videoElem_, 'timeupdate',
        this.timeUpdateThrottle_.fire, false, this.timeUpdateThrottle_);
};
mirosubs.Html5VideoPlayer.prototype.videoPlaying_ = function(event) {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PLAY);
};

mirosubs.Html5VideoPlayer.prototype.videoPaused_ = function(event) {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PAUSE);    
};

mirosubs.Html5VideoPlayer.prototype.videoProgress_ = function() {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PROGRESS);
};

mirosubs.Html5VideoPlayer.prototype.videoTimeUpdate_ = function() {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.TIMEUPDATE);
};
mirosubs.Html5VideoPlayer.prototype.getBufferedLength = function() {
    return this.videoElem_['buffered']['length'];
};
mirosubs.Html5VideoPlayer.prototype.getBufferedStart = function(index) {
    return this.videoElem_['buffered']['start'](index);
};
mirosubs.Html5VideoPlayer.prototype.getBufferedEnd = function(index) {
    return this.videoElem_['buffered']['end'](index);
};
mirosubs.Html5VideoPlayer.prototype.getDuration = function() {
    return this.videoElem_['duration'];
};
mirosubs.Html5VideoPlayer.prototype.isPaused = function() {
    return this.videoElem_['paused'];
};

mirosubs.Html5VideoPlayer.prototype.videoEnded = function() {
    return this.videoElem_['ended'];
};

mirosubs.Html5VideoPlayer.prototype.isPlaying = function() {
    var readyState = this.getReadyState_();
    var RS = mirosubs.Html5VideoPlayer.ReadyState_;
    return (readyState == RS.HAVE_FUTURE_DATA ||
            readyState == RS.HAVE_ENOUGH_DATA) &&
           !this.isPaused() && !this.videoEnded();
};

mirosubs.Html5VideoPlayer.prototype.play = function() {
    this.videoElem_['play']();
};

mirosubs.Html5VideoPlayer.prototype.pause = function() {
    this.videoElem_['pause']();
};

mirosubs.Html5VideoPlayer.prototype.getPlayheadTime = function() {
    return this.videoElem_["currentTime"];
};

mirosubs.Html5VideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    this.videoElem_["currentTime"] = playheadTime;
};

mirosubs.Html5VideoPlayer.prototype.getVideoSize = function() {
    return goog.style.getSize(this.videoElem_)
};

mirosubs.Html5VideoPlayer.prototype.getReadyState_ = function() {
    return this.videoElem_["readyState"];
};

mirosubs.Html5VideoPlayer.prototype.disposeInternal = function() {
    mirosubs.Html5VideoPlayer.superClass_.disposeInternal.call(this);
    this.progressThrottle_.dispose();
    this.timeUpdateThrottle_.dispose();
};

/**
 * See http://www.w3.org/TR/html5/video.html#dom-media-have_nothing
 * @enum
 */
mirosubs.Html5VideoPlayer.ReadyState_ = {
    HAVE_NOTHING  : 0,
    HAVE_METADATA : 1,
    HAVE_CURRENT_DATA : 2,
    HAVE_FUTURE_DATA : 3,
    HAVE_ENOUGH_DATA : 4
};