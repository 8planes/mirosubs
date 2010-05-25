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

goog.provide('mirosubs.video.AbstractVideoPlayer');

/**
 * Abstract base class for video player implementations. Any video player 
 * used with MiroSubs must implement the abstract methods defined by this 
 * class.
 * @constructor
 */
mirosubs.video.AbstractVideoPlayer = function(videoSource) {
    goog.ui.Component.call(this);
    this.videoSource_ = videoSource;
    this.noUpdateEvents_ = false;
};
goog.inherits(mirosubs.video.AbstractVideoPlayer, goog.ui.Component);
mirosubs.video.AbstractVideoPlayer.PROGRESS_INTERVAL = 500;
mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL = 80;

mirosubs.video.AbstractVideoPlayer.prototype.getPlayheadFn = function() {
    return goog.bind(this.getPlayheadTime, this);
};
mirosubs.video.AbstractVideoPlayer.prototype.createDom = function() {
    mirosubs.video.AbstractVideoPlayer.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-videoDiv';
};
mirosubs.video.AbstractVideoPlayer.prototype.isPaused = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.isPlaying = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.videoEnded = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.play = function(opt_suppressEvent) {
    if (!opt_suppressEvent)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PLAY_CALLED);
    this.playInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.playInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.pause = function(opt_suppressEvent) {
    if (!opt_suppressEvent)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.PAUSE_CALLED);
    this.pauseInternal();
};
mirosubs.video.AbstractVideoPlayer.prototype.pauseInternal = goog.abstractMethod;
mirosubs.video.AbstractVideoPlayer.prototype.togglePause = function() {
    if (!this.isPlaying())
        this.play();
    else
        this.pause();
};
mirosubs.video.AbstractVideoPlayer.prototype.getPlayheadTime = goog.abstractMethod;
/**
 * 
 *
 */
mirosubs.video.AbstractVideoPlayer.prototype.playWithNoUpdateEvents = 
    function(timeToStart, secondsToPlay) 
{
    this.noUpdateEvents_ = true;
    if (this.noUpdatePreTime_ == null)
        this.noUpdatePreTime_ = this.getPlayheadTime();
    this.setPlayheadTime(timeToStart);
    this.play();
    this.noUpdateStartTime_ = timeToStart;
    this.noUpdateEndTime_ = timeToStart + secondsToPlay;
};
mirosubs.video.AbstractVideoPlayer.prototype.sendTimeUpdateInternal = 
    function() 
{
    if (!this.noUpdateEvents_)
        this.dispatchEvent(
            mirosubs.video.AbstractVideoPlayer.EventType.TIMEUPDATE);
    else {
        if (this.ignoreTimeUpdate_)
            return;
        if (this.getPlayheadTime() >= this.noUpdateEndTime_) {
            this.ignoreTimeUpdate_ = true;
            this.setPlayheadTime(this.noUpdatePreTime_);
            this.noUpdatePreTime_ = null;
            this.pause();
            this.ignoreTimeUpdate_ = false;
            this.noUpdateEvents_ = false;
        }
    }
}
/**
 * @returns {number} video duration in seconds. Returns 0 if duration isn't
 *     available yet.
 */
mirosubs.video.AbstractVideoPlayer.prototype.getDuration = goog.abstractMethod;
/**
 * @returns {int} Number of buffered ranges.
 */
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedLength = goog.abstractMethod;
/**
 * @returns {number} Start of buffered range with index
 */
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedStart = function(index) {
    goog.abstractMethod();
};
mirosubs.video.AbstractVideoPlayer.prototype.getBufferedEnd = function(index) {
    goog.abstractMethod();
};
/**
 * @returns {number} 0.0 to 1.0
 */
mirosubs.video.AbstractVideoPlayer.prototype.getVolume = goog.abstractMethod;
/**
 * 
 * @param {number} volume A number between 0.0 and 1.0
 */
mirosubs.video.AbstractVideoPlayer.prototype.setVolume = function(volume) {
    goog.abstractMethod();
};
mirosubs.video.AbstractVideoPlayer.prototype.getVideoSource = function() {
    return this.videoSource_;
};
mirosubs.video.AbstractVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    goog.abstractMethod();
};
/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.video.AbstractVideoPlayer.prototype.showCaptionText = function(text) {
    if (text == null || text == "") {
        if (this.captionElem_ != null) {
            this.getElement().removeChild(this.captionElem_);
            this.captionElem_ = null;
            if (this.captionBgElem_ != null) {
                this.getElement().removeChild(this.captionBgElem_);
                this.captionBgElem_ = null;
            }
        }
    }
    else {
        var needsIFrame = this.needsIFrame();
        if (this.captionElem_ == null) {
            this.captionElem_ = document.createElement("div");
            this.captionElem_.setAttribute("class", "mirosubs-captionDiv");
            var videoSize = this.getVideoSize();
            this.captionElem_.style.top = (videoSize.height - 60) + "px";
            if (needsIFrame)
                this.captionElem_.style.visibility = 'hidden';
            this.getElement().appendChild(this.captionElem_);
        }
        goog.dom.setTextContent(this.captionElem_, text);
        if (needsIFrame) {
            var $d = goog.dom;
            var $s = goog.style;
            if (this.captionBgElem_ == null) {
                this.captionBgElem_ = document.createElement('iframe');
                this.captionBgElem_.setAttribute("class", "mirosubs-captionDivBg");
                this.captionBgElem_.style.visibility = 'hidden';
                this.captionBgElem_.style.top = this.captionElem_.style.top;
                // FIXME: get rid of hardcoded value
                this.captionBgElem_.style.left = "10px";
                $d.insertSiblingBefore(this.captionBgElem_, 
                                       this.captionElem_);
            }
            var size = $s.getSize(this.captionElem_);
            $s.setSize(this.captionBgElem_, size.width, size.height);
            this.captionBgElem_.style.visibility = 'visible';
            this.captionElem_.style.visibility = 'visible';
        }
    }
};
/**
 * Override for video players that need to show an iframe behind captions for 
 * certain browsers (e.g. flash on linux/ff)
 * @protected
 */
mirosubs.video.AbstractVideoPlayer.prototype.needsIFrame = function() {
    return false;
};
/**
 *
 * @protected
 * @return {goog.math.Size} size of the video
 */
mirosubs.video.AbstractVideoPlayer.prototype.getVideoSize = goog.abstractMethod;

/**
 * Video player events
 * @enum {string}
 */
mirosubs.video.AbstractVideoPlayer.EventType = {
    /** dispatched when playback starts or resumes. */
    PLAY : 'videoplay',
    PLAY_CALLED : 'videoplaycalled',
    /** dispatched when playback is paused. */
    PAUSE : 'videopause',
    PAUSE_CALLED : 'videopausecalled',
    /** dispatched when media data is fetched */
    PROGRESS : 'videoprogress',
    /** 
     * dispatched when playhead time changes, either as a result 
     *  of normal playback or otherwise. 
     */
    TIMEUPDATE : 'videotimeupdate'
};
