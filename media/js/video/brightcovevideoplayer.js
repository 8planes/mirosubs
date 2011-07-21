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

goog.provide('mirosubs.video.BrightcoveVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.BrightcoveVideoSource} videoSource
 * @param {boolean=} opt_forDialog
 */
mirosubs.video.BrightcoveVideoPlayer = function(videoSource, opt_forDialog) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);
    this.videoSource_ = videoSource;
    this.playerAPIID_ = [videoSource.getUUID()];
    this.playerElemID_ = videoSource.getUUID() + "_bcplayer";
    this.eventFunction_ = 'event' + videoSource.getUUID();
    this.forDialog_ = !!opt_forDialog;
    this.state_ = mirosubs.video.BrightcoveVideoPlayer.State_.UNSTARTED;
    var readyFunc = goog.bind(this.onBrightcoveTemplateLoaded_, this);
    var ytReady = "onTemplateLoaded";
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
goog.inherits(mirosubs.video.BrightcoveVideoPlayer, mirosubs.video.AbstractVideoPlayer);

/**
 * This decorates an Object or Embed element.
 * @override
 * @param {Element} element Either object or embed for yt video. Must 
 *     have enablejsapi=1.
 */
mirosubs.video.BrightcoveVideoPlayer.prototype.decorateInternal = function(element) {
    mirosubs.video.BrightcoveVideoPlayer.superClass_.decorateInternal.call(
        this, element);
    this.swfEmbedded_ = true;
    this.player_ = element;
    this.playerSize_ = goog.style.getSize(element);
    this.setDimensionsKnownInternal();
    // FIXME: petit duplication
    window[this.eventFunction_] = goog.bind(this.playerStateChange_, this);
    var timer = new goog.Timer(250);
    var that = this;
    var count = 0;
    this.getHandler().listen(
        timer,
        goog.Timer.TICK,
        function(e) {
            count++;
            if (count == 20)
                that.logExternalInterfaceError_();
            if (that.player_['play']) {
                timer.stop();
                that.player_.addEventListener(
                    'onStateChange', that.eventFunction_);
            }
        });
    timer.start();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.logExternalInterfaceError_ = function() {
    mirosubs.Rpc.call(
        'log_brightCove_ei_failure', { 'page_url': window.location.href });
};

mirosubs.video.BrightcoveVideoPlayer.prototype.createDom = function() {
    mirosubs.video.BrightcoveVideoPlayer.superClass_.createDom.call(this);
    var sizeFromConfig = this.sizeFromConfig_();
    if (!this.forDialog_ && sizeFromConfig)
        this.playerSize_ = sizeFromConfig;
    else
        this.playerSize_ = this.forDialog_ ?
        mirosubs.video.AbstractVideoPlayer.DIALOG_SIZE :
        mirosubs.video.AbstractVideoPlayer.DEFAULT_SIZE;    

};

mirosubs.video.BrightcoveVideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.BrightcoveVideoPlayer.superClass_.enterDocument.call(this);
    if (!this.swfEmbedded_) {
        this.swfEmbedded_ = true;
        var videoContainer = this.getDomHelper().createDom('div');
        

        var videoConf =  goog.object.clone(this.videoSource_.getVideoConfig());
        videoConf["playerID"] = this.videoSource_.getPlayerID();

        videoConf["playerKey"] = this.videoSource_.getPlayerKey();
        videoConf["videoID"] = this.videoSource_.getVideoID();
        videoConf["width"]  = videoConf["width"] || 480;
        videoConf["height"]  = videoConf["height"] || 412;
        videoConf['uuid'] = this.playerElemID_;
        var embedString = ' <object id="{{uuid}}" class="BrightcoveExperience"> <param name="bgcolor" value="#FFFFFF" /> <param name="width" value="{{width}}" /> <param name="height" value="{{height}}" /><param name="playerID" value="{{playerID}}" /><param name="playerKey" value="{{playerKey}}" /><param name="wmode" value="transparent" /><param name="isVid" value="true" /><param name="dynamicStreaming" value="true" /><param name="@videoPlayer" value="{{videoID}}" /></object>';

        for (var prop in videoConf){
            embedString = embedString.replace("{{"+prop+"}}", videoConf[prop]);
        }
        videoContainer.innerHTML = embedString;
        videoContainer.id = mirosubs.randomString();
        this.getElement().appendChild(videoContainer);
        brightcove.createExperiences();

    }
    this.getHandler().
        listen(this.progressTimer_, goog.Timer.TICK, this.progressTick_).
        listen(this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
    this.progressTimer_.start();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.sizeFromConfig_ = function() {
    var config = this.videoSource_.getVideoConfig();
    if (config && config['width'] && config['height'])
        return new goog.math.Size(
            parseInt(config['width']), parseInt(config['height']));
    else
        return null;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.exitDocument = function() {
    mirosubs.video.BrightcoveVideoPlayer.superClass_.exitDocument.call(this);
    this.progressTimer_.stop();
    this.timeUpdateTimer_.stop();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.progressTick_ = function(e) {
    if (this.getDuration() > 0)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PROGRESS);
};

mirosubs.video.BrightcoveVideoPlayer.prototype.timeUpdateTick_ = function(e) {
    if (this.getPlayheadTime() > 0)
        this.sendTimeUpdateInternal();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.onBrightcoveTemplateLoaded_ =
    function(playerAPIID)
{
    if (playerAPIID == this.playerElemID_) {
        this.setDimensionsKnownInternal();
        this.player_ = goog.dom.$(this.playerElemID_);
        this.bcPlayer_ = brightcove["getExperience"](this.playerElemID_);
        var experienceModule = this.bcPlayer_.getModule(APIModules.EXPERIENCE);
        experienceModule.addEventListener(BCExperienceEvent.TEMPLATE_READY, 
                                          goog.bind(this.onBrightcoveTemplateReady_, this));
        mirosubs.style.setSize(this.player_, this.playerSize_);
        goog.array.forEach(this.commands_, function(cmd) { cmd(); });
        this.commands_ = [];
    }
};

mirosubs.video.BrightcoveVideoPlayer.prototype.onBrightcoveTemplateReady_ = function(pEvent){
    var experienceModule = this.bcPlayer_.getModule(APIModules.EXPERIENCE);
    experienceModule.removeEventListener(BCExperienceEvent.TEMPLATE_READY, goog.bind(this.onBrightcoveTemplateReady_, this));
    this.bcPlayerController_ =  this.bcPlayer_.getModule(APIModules.VIDEO_PLAYER); 
    this.bcPlayerController_.addEventListener(
         BCMediaEvent.PLAY, goog.bind(this.onPlayerPlay_, this));
    this.bcPlayerController_.addEventListener(
         BCMediaEvent.STOP, goog.bind(this.onPlayerPause_, this));
    this.state_ = mirosubs.video.BrightcoveVideoPlayer.State_.BUFFERING;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.onPlayerPlay_ = function(e) {
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PLAY);
    this.timeUpdateTimer_.start();
    this.state_ = mirosubs.video.BrightcoveVideoPlayer.State_.PLAYING;
};

/*
 * @returns {bool} True if the video has ended.
 */
mirosubs.video.BrightcoveVideoPlayer.prototype.isFinished_ = function(){
    // the brightcove api will only fire COMPLETE events on the first
    // time the video plays, so a video can reach the end of the 
    // playhead without ever firing that event (if it was seeked back 
    // after completing once).
    
    return this.bcPlayerController_["getVideoDuration"]() - 
        this.bcPlayerController_["getVideoPosition"]() < 0.1;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.onPlayerPause_ = function(e) {
    this.dispatchEvent(mirosubs.video.AbstractVideoPlayer.EventType.PLAY);
    this.state_ = mirosubs.video.BrightcoveVideoPlayer.State_.PAUSED;
    this.timeUpdateTimer_.stop();
    if (this.isFinished_()) this.onPlayerComplete_();
    
};

mirosubs.video.BrightcoveVideoPlayer.prototype.onPlayerComplete_ = function(newState) {
    this.state_ = mirosubs.video.BrightcoveVideoPlayer.State_.ENDED;
    this.dispatchEndedEvent();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getBufferedLength = function() {
    return this.getDuration() > 0  ? 1 : 0;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getBufferedStart = function(index) {
    var startBytes = this.getStartBytes_();
    return this.getDuration() * startBytes / (startBytes + this.getBytesTotal_());
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getBufferedEnd = function(index) {
    var startBytes = this.getStartBytes_();
    return this.getDuration() *
        (startBytes + this.bcPlayerController_['getVideoBytesLoaded']()) /
        (startBytes + this.getBytesTotal_());
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getStartBytes_ = function() {
    return this.bcPlayerController_ ? this.bcPlayerController_['getVideoStartBytes']() : 0;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getBytesTotal_ = function() {
    return this.bcPlayerController_ ? this.bcPlayerController_.getVideoBytesTotal() : 0;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getDuration = function() {
    if (!this.duration_ && this.bcPlayerController_) {
        this.duration_ =  this.bcPlayerController_["getVideoDuration"]();
        if (this.duration_ <= 0)
            this.duration_ = 0;
    }
    return this.duration_;
};
mirosubs.video.BrightcoveVideoPlayer.prototype.getVolume = function() {
    return this.bcPlayerController_ ? (this.bcPlayerController_['getVolume']() / 100) : 0;
};
mirosubs.video.BrightcoveVideoPlayer.prototype.setVolume = function(vol) {
    if (this.bcPlayerController_)
        this.bcPlayerController_['setVolume'](vol * 100);
    else
        this.commands_.push(goog.bind(this.setVolume_, this, vol));
};
mirosubs.video.BrightcoveVideoPlayer.prototype.isPausedInternal = function() {
    return this.bcPlayerController_ && !this.bcPlayerController_["isPlaying"]();
};
mirosubs.video.BrightcoveVideoPlayer.prototype.videoEndedInternal = function() {
    return this.isFinished_();
};
mirosubs.video.BrightcoveVideoPlayer.prototype.isPlayingInternal = function() {
    return this.bcPlayerController_  && this.bcPlayerController_["isPlaying"]();
};
mirosubs.video.BrightcoveVideoPlayer.prototype.playInternal = function () {
    if (this.bcPlayerController_)
        this.bcPlayerController_['play']();
    else
        this.commands_.push(goog.bind(this.playInternal, this));
};
mirosubs.video.BrightcoveVideoPlayer.prototype.pauseInternal = function() {
    if (this.bcPlayerController_)
        this.bcPlayerController_['pause']();
    else
        this.commands_.push(goog.bind(this.pauseInternal, this));
};

mirosubs.video.BrightcoveVideoPlayer.prototype.stopLoadingInternal = function() {
    if (this.bcPlayerController_) {
        this.bcPlayerController_['stop']();
	this.setLoadingStopped(true);
	return true;	
    }
    else {
	this.commands_.push(goog.bind(this.stopLoadingInternal, this));
	return false;
    }
};

mirosubs.video.BrightcoveVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    if (this.bcPlayerController_) {
        this.bcPlayerController_['cueVideoById'](this.videoSource_.getBrightcoveVideoID(), playheadTime);
	this.setLoadingStopped(false);
    }
    else
        this.commands_.push(goog.bind(this.resumeLoadingInternal, this, playheadTime));
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getPlayheadTime = function() {
    return this.bcPlayerController_ ? this.bcPlayerController_['getVideoPosition']() : 0;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.setPlayheadTime = function(playheadTime)
{
    if (this.bcPlayerController_ ) {
        this.bcPlayerController_['seek'](playheadTime);
        this.sendTimeUpdateInternal();
    }
    else
        this.commands_.push(goog.bind(this.setPlayheadTime,
                                      this, playheadTime));
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getPlayerState_ = function() {
    return this.state_;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.needsIFrame = function() {
    return goog.userAgent.LINUX;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.isChromeless = function() {
    return false;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getVideoSize = function() {
    return this.playerSize_;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.BrightcoveVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
};

mirosubs.video.BrightcoveVideoPlayer.prototype.getVideoElement = function() {
    return this.player_;
};

mirosubs.video.BrightcoveVideoPlayer.prototype.toString = function() {
    return "BrightcoveVideoPlayer";
};

/**
 * http://code.google.com/apis/brightCove/js_api_reference.html#getPlayerState
 * @enum
 */
mirosubs.video.BrightcoveVideoPlayer.State_ = {
    UNSTARTED: -1,
    ENDED: 0,
    PLAYING: 1,
    PAUSED: 2,
    BUFFERING: 3,
    VIDEO_CUED: 5
};
