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

goog.provide('mirosubs.video.Html5VideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.Html5VideoSource} videoSource
 * @param {boolean} forDialog
 */
mirosubs.video.Html5VideoPlayer = function(videoSource, forDialog) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);

    this.videoSource_ = videoSource;
    this.videoElem_ = null;

    // only used in FF, since they don't support W3 buffered spec yet.
    this.videoLoaded_ = 0;
    this.videoTotal_ = 0;
    this.forDialog_ = forDialog;
    this.playToClick_ = false;

    this.progressThrottle_ = new goog.Throttle(
        this.videoProgress_,
        mirosubs.video.AbstractVideoPlayer.PROGRESS_INTERVAL,
        this);
    this.timeUpdateThrottle_ = new goog.Throttle(
        this.sendTimeUpdateInternal,
        mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL,
        this);
    this.playedOnce_ = false;
};
goog.inherits(mirosubs.video.Html5VideoPlayer,
              mirosubs.video.AbstractVideoPlayer);

mirosubs.video.Html5VideoPlayer.logger_ =
    goog.debug.Logger.getLogger('Html5VideoPlayer');

/**
 * @override
 */
mirosubs.video.Html5VideoPlayer.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    if (mirosubs.video.supportsVideoType(
        this.videoSource_.getVideoType())) {
        this.videoElem_ = this.createVideoElement_($d);
        this.setElementInternal(this.videoElem_);
        if (this.forDialog_)
            mirosubs.style.setSize(
                this.videoElem_,
                mirosubs.video.AbstractVideoPlayer.DIALOG_SIZE);
    }
    else {
        var el = $d('div');
        this.setElementInternal(el);
        mirosubs.style.setSize(el, 400, 300);
        mirosubs.style.setProperty(el, 'line-height', '300px');
        el.innerHTML = 
            "Sorry, your browser can't play HTML5/" + 
            this.videoSource_.getVideoType() + " video. " +
            "<a href='http://getfirefox.com'>Get Firefox</a>.";       
    }
};

/**
 * @override
 * @param {Element} element Video element to decorate.
 */
mirosubs.video.Html5VideoPlayer.prototype.decorateInternal = function(element) {
    mirosubs.video.Html5VideoPlayer.superClass_.decorateInternal.call(
        this, element);
    if (element.nodeName != 'VIDEO')
        throw Error(goog.ui.Component.Error.DECORATE_INVALID);
    this.videoElem_ = element;
};

mirosubs.video.Html5VideoPlayer.prototype.createVideoElement_ = 
    function($d) 
{
    var params = { 'autobuffer': 'true' };
    if (!this.forDialog_) {
        if (this.videoSource_.getVideoConfig()) {
            var config = this.videoSource_.getVideoConfig();
            if (config['play_to_click']) {
                this.playToClick_ = true;
                goog.object.remove(config, 'play_to_click');
            }
            goog.object.extend(params, config);
        }
        params['controls'] = 'true';
    }
    return $d('video', params,
              $d('source', {'src': this.videoSource_.getVideoURL()}));
};
mirosubs.video.Html5VideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.Html5VideoPlayer.superClass_.enterDocument.call(this);
    if (!this.videoElem_)
        return;
    this.getHandler().
        listen(this.videoElem_, 'play', this.videoPlaying_).
        listen(this.videoElem_, 'pause', this.videoPaused_).
        listen(this.videoElem_, 'progress', this.videoProgressListener_).
        listen(this.videoElem_, 'loadedmetadata', this.setDimensionsKnownInternal).
        listen(this.videoElem_, 'timeupdate', this.sendTimeUpdate_).
        listen(this.videoElem_, 'ended', this.dispatchEndedEvent).
        listenOnce(this.videoElem_, 'click', this.playerClicked_);
    if (this.videoElem_['readyState'] >= this.videoElem_['HAVE_METADATA']){
        
        this.setDimensionsKnownInternal();
    }
    this.restorePreviousVolume_();
    
};


mirosubs.video.Html5VideoPlayer.prototype.playerClicked_ = function(e) {
    if (this.playToClick_ && !this.playedOnce_) {
        e.preventDefault();
        this.play();
    }
};

mirosubs.video.Html5VideoPlayer.prototype.sendTimeUpdate_ = function() {
    if (this.playedOnce_)
        this.timeUpdateThrottle_.fire();
};

mirosubs.video.Html5VideoPlayer.prototype.setVideoSize = function(width, height) {
    mirosubs.style.setSize(this.videoElem_, width, height);
};

mirosubs.video.Html5VideoPlayer.prototype.videoPlaying_ = function(event) {
    this.playedOnce_ = true;
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PLAY);
};

mirosubs.video.Html5VideoPlayer.prototype.videoPaused_ = function(event) {
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PAUSE);
};

mirosubs.video.Html5VideoPlayer.prototype.videoProgressListener_ =
    function(event)
{
    if (event.getBrowserEvent()['loaded'] && event.getBrowserEvent()['total']) {
        this.videoLoaded_ = event.getBrowserEvent()['loaded'];
        this.videoTotal_ = event.getBrowserEvent()['total'];
        if (this.videoTotal_ == -1)
            this.videoTotal_ = this.videoLoaded_;
    }
    this.progressThrottle_.fire();
};

mirosubs.video.Html5VideoPlayer.prototype.videoProgress_ = function() {
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PROGRESS);
};

mirosubs.video.Html5VideoPlayer.prototype.getVolume = function() {
    return this.videoElem_['volume'];
};
mirosubs.video.Html5VideoPlayer.prototype.setVolume = function(volume) {
    this.videoElem_['volume'] = volume;
    mirosubs.video.Html5VideoPlayer.superClass_.setVolume.call(this, volume);
    
};
mirosubs.video.Html5VideoPlayer.prototype.getBufferedLength = function() {
    if (this.videoElem_['buffered'])
        return this.videoElem_['buffered']['length'];
    else
        return this.videoTotal_ == 0 ? 0 : 1;
};
mirosubs.video.Html5VideoPlayer.prototype.getBufferedStart = function(index) {
    if (this.videoElem_['buffered'])
        return this.videoElem_['buffered']['start'](index);
    else
        return 0;
};
mirosubs.video.Html5VideoPlayer.prototype.getBufferedEnd = function(index) {
    if (this.videoElem_['buffered'])
        return this.videoElem_['buffered']['end'](index);
    else if (this.videoTotal_ != 0 && this.getDuration() != 0)
        return this.getDuration() * this.videoLoaded_ / this.videoTotal_;
    else
        return 0;
};
mirosubs.video.Html5VideoPlayer.prototype.getDuration = function() {
    var duration = this.videoElem_['duration'];
    return isNaN(duration) ? 0 : duration;
};
mirosubs.video.Html5VideoPlayer.prototype.isPausedInternal = function() {
    return this.videoElem_['paused'];
};

mirosubs.video.Html5VideoPlayer.prototype.videoEndedInternal = function() {
    return this.videoElem_['ended'];
};

mirosubs.video.Html5VideoPlayer.prototype.isPlayingInternal = function() {
    var readyState = this.getReadyState_();
    var RS = mirosubs.video.Html5VideoPlayer.ReadyState_;
    return (readyState == RS.HAVE_FUTURE_DATA ||
            readyState == RS.HAVE_ENOUGH_DATA) &&
           !this.isPaused() && !this.videoEnded();
};

mirosubs.video.Html5VideoPlayer.prototype.playInternal = function() {
    this.videoElem_['play']();
};

mirosubs.video.Html5VideoPlayer.prototype.pauseInternal = function() {
    this.videoElem_['pause']();
};

mirosubs.video.Html5VideoPlayer.prototype.stopLoadingInternal = function() {
    // TODO: replace this with an actual URL
    this.videoElem_['src'] = 'http://holmeswilson.org/tinyblank.ogv';
    return true;
};

mirosubs.video.Html5VideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    this.videoElem_['src'] = this.videoSource_.getVideoURL();
    this.setLoadingStopped(false);
    this.setPlayheadTime(playheadTime);
    this.pause();
};

mirosubs.video.Html5VideoPlayer.prototype.getPlayheadTimeInternal = function() {
    return this.videoElem_["currentTime"];
};

mirosubs.video.Html5VideoPlayer.prototype.setPlayheadTime = function(playheadTime, skipsUpdateEvent) {
    try{
        this.videoElem_["currentTime"] = playheadTime;
    }catch(e){
        // this migth fail if we have not loaded metadata yet
    }
    
};

mirosubs.video.Html5VideoPlayer.prototype.getVideoSize = function() {
    return goog.style.getSize(this.videoElem_);
};

mirosubs.video.Html5VideoPlayer.prototype.getVideoElements = function() {
    return [this.videoElem_];
};

mirosubs.video.Html5VideoPlayer.prototype.getReadyState_ = function() {
    return this.videoElem_["readyState"];
};

mirosubs.video.Html5VideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.Html5VideoPlayer.superClass_.disposeInternal.call(this);
    this.progressThrottle_.dispose();
    this.timeUpdateThrottle_.dispose();
};

/**
 * See http://www.w3.org/TR/html5/video.html#dom-media-have_nothing
 * @enum
 */
mirosubs.video.Html5VideoPlayer.ReadyState_ = {
    HAVE_NOTHING  : 0,
    HAVE_METADATA : 1,
    HAVE_CURRENT_DATA : 2,
    HAVE_FUTURE_DATA : 3,
    HAVE_ENOUGH_DATA : 4
};
